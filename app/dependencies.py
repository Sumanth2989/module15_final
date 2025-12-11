from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.auth import decode_access_token # This imports from app/auth.py

# auto_error=False allows us to check the cookie manually if the header is missing
security = HTTPBearer(auto_error=False)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = None
    
    # 1. Try to get token from the Authorization Header (for Tests/API)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # 2. If no header, try to get from the Cookie (for Browser)
    if not token:
        token = request.cookies.get("access_token")
    
    # 3. If still no token, you are not logged in
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )

    # 4. Check if the token is valid
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    return user