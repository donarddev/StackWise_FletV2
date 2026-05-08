"""AuthenticationService — login & registration business logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.helpers.hash_helper import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.requests.login_request import LoginRequest
from app.requests.register_request import RegisterRequest


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
