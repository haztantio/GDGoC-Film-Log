import re
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from .. import models, utils

# Pembatasan percobaan login
login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = timedelta(minutes=1)

def register_new_user(db: Session, user_data):
    """Cek email, hash password, dan simpan user baru ke database."""
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
    
    # password security
    password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$"
    if not re.match(password_regex, user_data.password):
        error_message = "Your password must contain at least 8 characters, including uppercase and lowercase letters, numbers, and special symbols!"
        return JSONResponse(
            status_code=422,
            content={
                "detail": error_message,
                "message": error_message
            }
        )

    # enkripsi password sebelum ke database
    hashed_password = utils.get_password_hash(user_data.password)
    new_user = models.User(
        email=user_data.email, 
        username=user_data.username, 
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, email: str, password: str):
    """Hitung percobaan login dan validasi kredensial"""
    now = datetime.now()
    
    rate_limit_error = JSONResponse(
        status_code=429, 
        content={
            "detail": "Too many failed attempts. Please wait 1 minute.",
            "message": "Too many failed attempts. Please wait 1 minute."
        }
    )

    # Cek percobaan login
    if email in login_attempts:
        attempts = login_attempts[email]
        if attempts['count'] >= MAX_ATTEMPTS:
            if now < attempts['lock_until']:
                return rate_limit_error  
            else:
                login_attempts.pop(email, None) 

    # Validasi kredensial
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user or not utils.verify_password(password, user.password_hash):
        if email not in login_attempts:
            login_attempts[email] = {'count': 1, 'lock_until': now}
        else:
            login_attempts[email]['count'] += 1
            if login_attempts[email]['count'] >= MAX_ATTEMPTS:
                login_attempts[email]['lock_until'] = now + LOCKOUT_TIME
                return rate_limit_error  
        
        return JSONResponse(
            status_code=403, 
            content={
                "detail": "Invalid email or password",
                "message": "Invalid email or password",
                "error": "Invalid email or password"
            }
        )

    login_attempts.pop(email, None)
    return user