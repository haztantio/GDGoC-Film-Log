import os
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# KONFIGURASI KEAMANAN
# ==========================================
SECRET_KEY = os.getenv("SECRET_KEY", "rahasia_default_jika_env_gagal_terbaca")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Tiket (Token) akan hangus dalam 7 hari

# Menyalakan mesin pengacak (Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================================
# FUNGSI-FUNGSI LOGIKA (SERVICE)
# ==========================================

# 1. Mengacak Password (Dipakai saat REGISTER)
def get_password_hash(password: str) -> str:
    """Mengubah teks asli ('qwerty') menjadi teks acak ('$2b$12$R9h...')"""
    return pwd_context.hash(password)

# 2. Mengecek Password (Dipakai saat LOGIN)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Mencocokkan password yang diketik dengan hasil acakan di database"""
    return pwd_context.verify(plain_password, hashed_password)

# 3. Membuat Tiket Masuk / Token (Dipakai saat LOGIN BERHASIL)
def create_access_token(data: dict) -> str:
    """Membungkus data user (seperti ID dan Email) menjadi satu token JWT panjang"""
    to_encode = data.copy()
    
    # Tentukan kapan token ini kadaluarsa
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Segel token menggunakan kunci rahasia dari .env
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt