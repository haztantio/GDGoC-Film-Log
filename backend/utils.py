import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

# 1. Konfigurasi Pengacak Password (Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Konfigurasi Kunci Token (JWT)
# Mengambil dari .env jika ada, atau menggunakan kunci cadangan
SECRET_KEY = os.getenv("SECRET_KEY", "kunci-rahasia-gdgoc-ugm-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # Token berlaku 24 jam

def hash_password(password: str):
    """Mengacak password sebelum disimpan ke database"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Mengecek apakah password yang diketik sama dengan di database"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Membuat tiket (token) saat user berhasil login"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt