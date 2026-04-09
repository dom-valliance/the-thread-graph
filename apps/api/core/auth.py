from __future__ import annotations

from fastapi import Depends, Request

from core.config import Settings
from core.dependencies import get_settings


async def get_current_user(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> str:
    """Resolve the current user from the request.

    When authentication is disabled, returns a development identity.
    When enabled, extracts the Bearer token from the Authorization header.
    Full Azure AD JWT validation is future work.
    """
    if not settings.auth_enabled:
        return "dev@valliance.ai"

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        from core.exceptions import ValidationError

        raise ValidationError("Missing or malformed Authorization header")

    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        from core.exceptions import ValidationError

        raise ValidationError("Empty Bearer token")

    # Placeholder: return the token as the user identity.
    # Replace with Azure AD JWT decode and validation.
    return token
