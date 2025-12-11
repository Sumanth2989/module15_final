# app/dependencies.py
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db import get_db
from app.models.user import User
from app.auth import SECRET_KEY, ALGORITHM


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Resolve the current user from either:
    - Authorization: Bearer <token> header (used by integration tests)
    - access_token cookie (set by the /login form flow)

    Raises 401 if no valid token is found.
    """
    token = None

    # 1. Try Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    # 2. Fallback to cookie if header missing
    if not token:
        cookie_val = request.cookies.get("access_token")
        if cookie_val:
            if cookie_val.lower().startswith("bearer "):
                token = cookie_val.split(" ", 1)[1].strip()
            else:
                token = cookie_val.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
