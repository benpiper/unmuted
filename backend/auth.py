import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
import bcrypt
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import User
from database import get_db
import time

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable must be set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

_token_blacklist = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    import uuid
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire_timestamp = expire.timestamp()
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def initialize_admin_from_env(db: AsyncSession):
    """Initialize first admin from environment variables if they exist."""
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

    if not admin_email:
        return False

    existing_user = await get_user_by_email(db, admin_email)
    if existing_user:
        return False

    result = await db.execute(select(func.count(User.id)))
    user_count = result.scalar()
    if user_count > 0:
        return False

    if admin_password_hash:
        hashed = admin_password_hash
    elif admin_password:
        hashed = get_password_hash(admin_password)
    else:
        return False

    admin_user = User(
        email=admin_email,
        hashed_password=hashed,
        is_approved=True,
        is_admin=True
    )
    db.add(admin_user)
    await db.commit()
    return True

def _cleanup_blacklist():
    """Remove expired tokens from blacklist."""
    now = time.time()
    expired = [jti for jti, exp_time in _token_blacklist.items() if exp_time < now]
    for jti in expired:
        del _token_blacklist[jti]

def revoke_token(jti: str, exp_time: float):
    """Add token to blacklist."""
    _cleanup_blacklist()
    _token_blacklist[jti] = exp_time

def is_token_revoked(jti: str) -> bool:
    """Check if token is revoked."""
    return jti in _token_blacklist

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise credentials_exception

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        jti: str = payload.get("jti")
        if email is None:
            raise credentials_exception
        if jti and is_token_revoked(jti):
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user
