from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

# Dependency to extract and verify Firebase ID token
def get_current_user(credential: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False))):
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required",
            headers={'WWW-Authenticate': 'Bearer'},
        )
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(credential.credentials)
        print(decoded_token)
        return decoded_token
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token. Details: {err}",
            headers={'WWW-Authenticate': 'Bearer error="invalid_token"'},
        )
