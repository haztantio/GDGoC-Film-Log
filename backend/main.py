from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import auth_router, movie_router, watch_router

# Cek ketersediaan tabel di database
models.Base.metadata.create_all(bind=engine)

# Inisialisasi FastAPI
app = FastAPI(
    title="Movie Watchlist REST API",
    description="Backend service untuk mengelola film, watchlist, rating",
    version="1.0"
)

# Menambahkan CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow akses port frontend
    allow_credentials=True,
    allow_methods=["*"],  # allow GET, POST, PUT, DELETE
    allow_headers=["*"],  # allow header Authorization
)

app.include_router(auth_router.router, prefix="/api")
app.include_router(movie_router.router, prefix="/api")
app.include_router(watch_router.router, prefix="/api")

# Endpoint root untuk cek server
@app.get("/")
def read_root():
    return {
        "status": "sukses",
        "pesan": "Backend server berjalan dengan baik"
    }