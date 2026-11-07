from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .. import schemas, utils
from ..database import get_db
from ..services import auth_service

# Router untuk autentikasi register & login
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Endpoint /api/auth/register (POST)
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Mendaftarkan pengguna baru dengan aturan keamanan password yang ketat."""
    result = auth_service.register_new_user(db, user_data)
    return result

# Endpoint /api/auth/login (POST)
@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """user login, validasi limit 5x, dan return JWT"""
    user_or_error = auth_service.authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if isinstance(user_or_error, JSONResponse):
        return user_or_error
        
    # akses token JWT dibuat di utils.py
    access_token = utils.create_access_token(data={"user_id": user_or_error.id})
    
    return {
        "access_token": access_token,
        "token": access_token,
        "token_type": "bearer",
        "user": {"id": user_or_error.id, "email": user_or_error.email}
    }