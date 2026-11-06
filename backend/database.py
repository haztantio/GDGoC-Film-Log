import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 1. Muat variabel rahasia dari file .env
load_dotenv()

# 2. Ambil URL koneksi PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Nyalakan mesin penghubung (Engine) ke database
engine = create_engine(DATABASE_URL)

# 4. Buat pabrik sesi (SessionLocal) untuk setiap request yang masuk
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Buat fondasi dasar (Base) untuk rancangan tabel kita nanti
Base = declarative_base()

# 6. Fungsi pembantu untuk membuka dan menutup koneksi database secara otomatis
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()