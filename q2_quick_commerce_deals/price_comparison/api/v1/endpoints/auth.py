"""Authentication API endpoints for the price comparison platform."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from ...database.base import get_db
from ...core.config import settings

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.security.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

@router.post("/login", response_model=Token, summary="User login")
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token."""
    # Mock authentication - in production, verify against database
    if user_credentials.email == "demo@example.com" and user_credentials.password == "password":
        access_token_expires = timedelta(minutes=settings.security.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_credentials.email, "user_id": 1},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.security.access_token_expire_minutes * 60
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=Token, summary="User registration")
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register new user and return JWT token."""
    # Mock registration - in production, save to database
    hashed_password = get_password_hash(user_data.password)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.security.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user_data.email, "user_id": 2},  # Mock user ID
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.security.access_token_expire_minutes * 60
    }

@router.post("/refresh", response_model=Token, summary="Refresh token")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh JWT token."""
    try:
        payload = jwt.decode(credentials.credentials, settings.security.secret_key, algorithms=[settings.security.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Create new token
        access_token_expires = timedelta(minutes=settings.security.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": email, "user_id": payload.get("user_id")},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.security.access_token_expire_minutes * 60
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me", summary="Get current user")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user information."""
    try:
        payload = jwt.decode(credentials.credentials, settings.security.secret_key, algorithms=[settings.security.algorithm])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "email": email,
            "user_id": user_id,
            "is_authenticated": True
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token") 