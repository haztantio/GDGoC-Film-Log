from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from . import models, utils
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Pastikan menggunakan SECRET_KEY dan ALGORITHM dari utils.py
        payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        
        # 2. Pastikan mencari "user_id"
        user_id = payload.get("user_id") 
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    # 3. Cari user di database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user