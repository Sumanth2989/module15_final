from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User

# --- CONFIGURATION ---
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- HASHING TOOLS ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# We define this function as 'get_password_hash'
def get_password_hash(password):
    # Defensive: ensure password is a string and does not exceed bcrypt's 72-byte limit.
    if not isinstance(password, (str, bytes, bytearray)):
        # convert unusual inputs (e.g., None or dict) to string representation
        password = str(password)

    if isinstance(password, str):
        pw_bytes = password.encode('utf-8')
    else:
        pw_bytes = bytes(password)

    # bcrypt has a 72-byte input limit; truncate to avoid ValueError from underlying driver
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]
        try:
            password = pw_bytes.decode('utf-8')
        except Exception:
            # fallback: use latin-1 to preserve byte values
            password = pw_bytes.decode('latin-1')

    return pwd_context.hash(password)

# --- THE FIX: ALIAS ---
# This line makes 'hash_password' point to the same tool.
# Now both names work!
hash_password = get_password_hash

# --- AUTHENTICATION LOGIC ---
def authenticate_user(db: Session, username: str, password: str):
    # We use 'email' as the username
    user = db.query(User).filter(User.email == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# --- TOKEN TOOLS ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None