"""GoogleAuthService — handles OAuth HTTP interactions with Google.

Uses Web OAuth (authorization code flow) and returns a normalized profile
dictionary. Does not persist tokens.
"""

from __future__ import annotations

import os
import secrets
import threading
import time
from typing import Optional

import httpx
from urllib.parse import urlencode

from app.utils.logger import get_logger

log = get_logger(__name__)
_OAUTH_STATE_TTL_SECONDS = 600
_oauth_states: dict[str, dict[str, object]] = {}
_oauth_states_lock = threading.Lock()


class GoogleAuthError(RuntimeError):
    pass


class GoogleAuthService:
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(self) -> None:
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

        if not (self.client_id and self.client_secret and self.redirect_uri):
            log.debug("Google OAuth env vars not fully configured.")

    def build_authorization_url(self, state: Optional[str] = None) -> str:
        # Ensure required config present
        if not (self.client_id and self.client_secret and self.redirect_uri):
            raise GoogleAuthError(
                "Google OAuth is not configured. Please check GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI in your .env file."
            )

        state = state or secrets.token_urlsafe(32)
        self._store_oauth_state(state)
        log.info("Google OAuth started")
        log.info("Google OAuth state prefix: %s", state[:8])
        log.info("Google OAuth redirect URI: %s", self.redirect_uri)
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": self.redirect_uri,
            "state": state,
            "prompt": "select_account",
            "access_type": "offline",
            "include_granted_scopes": "true",
        }

        qs = urlencode(params)
        return f"{self.AUTH_URL}?{qs}"

    def _store_oauth_state(self, state: str) -> None:
        now = time.time()
        with _oauth_states_lock:
            # Opportunistic cleanup to keep memory bounded.
            expired = [
                s for s, payload in _oauth_states.items()
                if float(payload.get("expires_at", 0)) < now
            ]
            for stale in expired:
                _oauth_states.pop(stale, None)
            _oauth_states[state] = {
                "created_at": now,
                "expires_at": now + _OAUTH_STATE_TTL_SECONDS,
                "redirect_after_login": "/dashboard",
            }

    def validate_oauth_state(self, returned_state: Optional[str]) -> Optional[dict[str, object]]:
        if not returned_state:
            return None
        now = time.time()
        with _oauth_states_lock:
            state_payload = _oauth_states.pop(returned_state, None)  # one-time use
        if state_payload is None:
            return None
        if float(state_payload.get("expires_at", 0)) < now:
            return None
        return state_payload

    def exchange_code_for_profile(self, code: str) -> dict:
        if not (self.client_id and self.client_secret and self.redirect_uri):
            raise GoogleAuthError("Google OAuth is not configured on the server.")

        # Exchange code for tokens
        try:
            with httpx.Client(timeout=10.0) as client:
                token_resp = client.post(
                    self.TOKEN_URL,
                    data={
                        "code": code,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": self.redirect_uri,
                        "grant_type": "authorization_code",
                    },
                )
                token_resp.raise_for_status()
                token_data = token_resp.json()

                access_token = token_data.get("access_token")
                if not access_token:
                    raise GoogleAuthError("No access token returned from Google.")
                log.info("Google OAuth token exchange succeeded")

                # Fetch userinfo
                user_resp = client.get(self.USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
                user_resp.raise_for_status()
                info = user_resp.json()
                log.info("Google OAuth email received: %s", info.get("email"))

                profile = {
                    "google_id": info.get("sub"),
                    "email": info.get("email"),
                    "name": info.get("name") or info.get("given_name"),
                    "avatar_url": info.get("picture"),
                }
                return profile
        except httpx.HTTPError as exc:
            log.error("Google OAuth HTTP error: %s", exc)
            raise GoogleAuthError("Failed to communicate with Google.") from exc
