from dataclasses import dataclass
from hashlib import sha256

from services.auth_service.schemas import DemoUser


@dataclass(frozen=True)
class AuthResult:
    user: DemoUser | None
    error_code: str | None = None


class AuthService:
    """Local-only token fixture; replace with a verified identity provider in production."""

    def __init__(self) -> None:
        self._active_tokens = {
            sha256(b"demo-admin-token").hexdigest(): DemoUser(
                user_id="demo-admin",
                display_name="Demo Administrator",
                role="admin",
            ),
            sha256(b"demo-operator-token").hexdigest(): DemoUser(
                user_id="demo-operator",
                display_name="Demo Operator",
                role="operator",
            ),
            sha256(b"demo-viewer-token").hexdigest(): DemoUser(
                user_id="demo-viewer",
                display_name="Demo Viewer",
                role="viewer",
            ),
        }
        self._expired_tokens = {sha256(b"demo-expired-token").hexdigest()}

    def validate(self, token: str) -> AuthResult:
        token_hash = sha256(token.encode()).hexdigest()
        user = self._active_tokens.get(token_hash)
        if user is not None:
            return AuthResult(user=user)
        if token_hash in self._expired_tokens:
            return AuthResult(user=None, error_code="credential_expired")
        return AuthResult(user=None, error_code="invalid_credentials")


ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "admin": frozenset({"metrics:read", "users:read", "admin:read", "operations:read"}),
    "operator": frozenset({"metrics:read", "users:read", "operations:read"}),
    "viewer": frozenset({"metrics:read", "users:read"}),
}


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())
