import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from dotenv import load_dotenv

# Bagian fungsi hash, verifikasi password, dan membuat JWT token
load_dotenv()

# Enkripsi password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Konfigurasi JWT token
SECRET_KEY = os.getenv("SECRET_KEY", "kunci-rahasia-gdgoc-ugm-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Token berlaku 7 hari

def get_password_hash(password: str) -> str:
    """Hash password sebelum disimpan ke database"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi hash password dengan database"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Membuat JWT token jika user berhasil login"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)