import re
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
from ..services import auth_service
from fastapi.security import OAuth2PasswordRequestForm


# Membuat router khusus untuk urusan login dan registrasi
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Sistem pelacak percobaan login (Rate Limiting In-Memory)
login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = timedelta(minutes=1)

# ==========================================
# 1. Endpoint REGISTER (Mendaftar akun baru)
# ==========================================
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Cek apakah email sudah dipakai pengguna lain
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Email already registered",
                "message": "Email already registered",
                "error": "Email already registered"
            }
        )
    password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$"
    
    if not re.match(password_regex, user_data.password):
        error_message = "Your password must contain at least 8 characters, including uppercase and lowercase letters, numbers, and special symbols."
        return JSONResponse(
            status_code=422,
            content={
                "detail": error_message,
                "message": error_message
            }
        )

    # 2. Ambil fungsi hash password dari auth_service (koki kita)
    hashed_password = auth_service.get_password_hash(user_data.password)
    
    # 3. Rakit data pengguna baru sesuai cetak biru models.py
    new_user = models.User(email=user_data.email, username=user_data.username, password_hash=hashed_password)
    
    # 4. Simpan permanen ke PostgreSQL
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# ==========================================
# UBAH BAGIAN INI (Ganti form_data menjadi user_credentials)
# ==========================================
@router.post("/login")
def login(
    user_credentials: schemas.UserLogin, # Sesuaikan dengan nama skemamu
    db: Session = Depends(get_db)
):
    email = user_credentials.email
    now = datetime.now()

    # 1. Cek apakah akun ini sedang dalam masa hukuman (lockout)
    if email in login_attempts:
        attempts = login_attempts[email]
        if attempts['count'] >= MAX_ATTEMPTS:
            if now < attempts['lock_until']:
                raise JSONResponse(
                    status_code=429, 
                    content={
                        "detail": "Too many failed attempts. Please wait 1 minute.",
                        "message": "Too many failed attempts. Please wait 1 minute."
                    }
                )
            else:
                # Waktu hukuman habis, hapus catatan buruknya
                login_attempts.pop(email, None)

    # 2. Cari user di database
    user = db.query(models.User).filter(models.User.email == email).first()

    # 3. Cek validitas (jika gagal, catat percobaannya)
    if not user or not utils.verify_password(user_credentials.password, user.password_hash):
        if email not in login_attempts:
            login_attempts[email] = {'count': 1, 'lock_until': now}
        else:
            login_attempts[email]['count'] += 1
            if login_attempts[email]['count'] >= MAX_ATTEMPTS:
                login_attempts[email]['lock_until'] = now + LOCKOUT_TIME
                raise JSONResponse(
                    status_code=429, 
                    content={
                        "detail": "Too many failed attempts. Please wait 1 minute.",
                        "message": "Too many failed attempts. Please wait 1 minute."
                    }
                )
        
        # Pesan kustom sesuai permintaanmu
        # Mengirimkan 3 nama kunci sekaligus agar ada yang 'nyangkut' di frontend
        return JSONResponse(
            status_code=403, 
            content={
                "detail": "Invalid email or password",
                "message": "Invalid email or password",
                "error": "Invalid email or password"
            }
        )

    # 4. Jika berhasil login, bersihkan catatan kegagalannya
    login_attempts.pop(email, None)

    # 5. Buat token (Sama seperti sebelumnya)
    access_token = utils.create_access_token(data={"user_id": user.id})
    return {
        "access_token": access_token,
        "token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email}
    }