"""AuthenticationService — login & registration business logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.helpers.hash_helper import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.requests.login_request import LoginRequest
from app.requests.register_request import RegisterRequest
from app.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class AuthResult:
    success: bool
    user: Optional[User] = None
    errors: dict[str, str] = None  # type: ignore[assignment]
    message: Optional[str] = None


class AuthenticationService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.users = user_repository

    def login(self, request: LoginRequest) -> AuthResult:
        errors = request.validate()
        if errors:
            return AuthResult(success=False, errors=errors, message="Please fix the errors above.")

        user = self.users.find_by_email_or_username(request.identifier)
        if user is None or not verify_password(request.password, user.password_hash):
            return AuthResult(
                success=False,
                errors={},
                message="Those credentials do not match any account.",
            )

        return AuthResult(success=True, user=user, errors={})

    def register(self, request: RegisterRequest) -> AuthResult:
        errors = request.validate()
        if errors:
            return AuthResult(success=False, errors=errors, message="Please fix the errors above.")

        if self.users.find_by_email(request.email) is not None:
            return AuthResult(
                success=False,
                errors={"email": "That email is already registered."},
                message="That email is already registered.",
            )
        if self.users.find_by_username(request.username) is not None:
            return AuthResult(
                success=False,
                errors={"username": "Username is taken."},
                message="Username is taken.",
            )

        user = self.users.create(
            full_name=request.full_name,
            username=request.username,
            email=request.email,
            password_hash=hash_password(request.password),
        )
        return AuthResult(success=True, user=user, errors={})

    def authenticate_google_user(self, profile: dict) -> AuthResult:
        """Authenticate or create a user using Google profile data.

        Profile must contain `google_id` and `email` at minimum.
        """
        google_id = profile.get("google_id")
        email = profile.get("email")
        if not google_id or not email:
            return AuthResult(success=False, errors={}, message="Invalid Google profile.")

        # 1) Try find by google_id
        user = self.users.find_by_google_id(google_id)
        if user is not None:
            log.info("Google OAuth user found by google_id: %s", user.email)
            return AuthResult(success=True, user=user, errors={})

        # 2) Try find by email and link
        user = self.users.find_by_email(email)
        if user is not None:
            self.users.link_google_account(user.id, google_id, profile.get("avatar_url"))
            log.info("Google OAuth existing email linked: %s", user.email)
            # reload user
            user = self.users.find_by_id(user.id)
            return AuthResult(success=True, user=user, errors={})

        # 3) Create a new google user
        name = profile.get("name") or ""
        created = self.users.create_google_user(
            full_name=name,
            email=email,
            google_id=google_id,
            avatar_url=profile.get("avatar_url"),
        )
        log.info("Google OAuth user created: %s", created.email)
        return AuthResult(success=True, user=created, errors={})
