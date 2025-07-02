# In a real application, this would contain functions for handling
# authentication (e.g., JWT validation, API key checks).

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-api-key"  # Replace with a secure key from env vars
API_KEY_NAME = "X-API-KEY"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
