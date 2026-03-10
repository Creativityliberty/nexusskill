import secrets
import hashlib
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)

def generate_api_key() -> str:
    """Generate a clean, secure API key."""
    return f"nx_{secrets.token_urlsafe(32)}"

def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()

async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    if api_key_header:
        # In Phase 1, we might have a hardcoded key or check DB
        # This is a placeholder for actual DB validation
        return api_key_header
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate API Key",
    )
