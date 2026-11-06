from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import auth_router, movie_router, watch_router

# 1. Perintah ini akan menyuruh SQLAlchemy mengecek PostgreSQL. 
# Jika tabel belum ada, ia akan otomatis membuatnya berdasarkan cetak biru di models.py
models.Base.metadata.create_all(bind=engine)

# 2. Inisialisasi Aplikasi FastAPI
app = FastAPI(
    title="Movie Watchlist REST API",
    description="Backend service untuk mengelola film, watchlist, rating",
    version="1.0"
)

# 2. Tambahkan pengaturan CORS di bawah app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mengizinkan akses dari semua port frontend (Live Server, React, dll)
    allow_credentials=True,
    allow_methods=["*"],  # Mengizinkan semua metode (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Mengizinkan pengiriman token JWT di header
)

app.include_router(auth_router.router, prefix="/api")
app.include_router(movie_router.router, prefix="/api")
app.include_router(watch_router.router, prefix="/api")

# 3. Rute Uji Coba (Akar URL)
@app.get("/")
def read_root():
    return {
        "status": "sukses",
        "pesan": "Selamat! Server Backend kamu sudah menyala dan terhubung ke database."
    }