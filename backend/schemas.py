from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ==========================================
# 1. SKEMA TOKEN (Untuk Login)
# ==========================================
class Token(BaseModel):
    access_token: str
    token_type: str

# ==========================================
# 2. SKEMA USER (Pengguna)
# ==========================================
# Skema saat user mengirim data dari form pendaftaran (hanya butuh email & password)
class UserCreate(BaseModel):
    email: EmailStr  # Otomatis menolak jika format email salah (misal: tanpa '@')
    password: str # Password minimal 8 karakter
    username: str

class UserLogin(BaseModel):
    email: str
    password: str

# Skema saat backend mengembalikan data user (Password TIDAK BOLEH dikembalikan!)
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_time: datetime

    model_config = {"from_attributes": True} # Penting: Agar Pydantic bisa membaca data dari SQLAlchemy

# ==========================================
# 3. SKEMA MOVIE (Film)
# ==========================================
class MovieResponse(BaseModel):
    id: int
    title: str
    year: Optional[int] = None
    director: Optional[str] = None
    genres: Optional[str] = None
    rating: Optional[float] = None
    duration: Optional[str] = None
    synopsis: Optional[str] = None
    poster_url: Optional[str] = None
    cast: Optional[str] = None

    model_config = {"from_attributes": True}

# Menerima ID Film, angka bintang, dan teks ulasan dari frontend
class WatchedCreate(BaseModel):
    movie_id: int
    rating: int
    review: str | None = None

# Mengirim kembali data ulasan beserta detail filmnya ke frontend
class WatchedResponse(BaseModel):
    id: int
    movie_id: int
    rating: int
    review: str | None = None  # <--- UBAH text_review MENJADI review
    watched_time: datetime | None = None  # (Atau format waktu yang kamu gunakan)
    movie: MovieResponse

    class Config:
        from_attributes = True

# ==========================================
# 4. SKEMA WATCHLIST (Daftar Tontonan)
# ==========================================
class WatchlistCreate(BaseModel):
    movie_id: int

class WatchlistResponse(BaseModel):
    id: int
    movie_id: int
    added_time: datetime
    movie: MovieResponse # Otomatis melampirkan detail film di dalam JSON

    model_config = {"from_attributes": True}

# ==========================================
# 5. SKEMA REVIEWS (Ulasan / Watched)
# ==========================================
class ReviewCreate(BaseModel):
    movie_id: int
    rating: int = Field(..., ge=1, le=5)  # Validasi: 'ge' (Greater/Equal 1), 'le' (Less/Equal 5)
    review: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    movie_id: int
    rating: int
    review: Optional[str]
    watched_time: datetime
    movie: MovieResponse

    model_config = {"from_attributes": True}

# ==========================================
# SCHEMA UNTUK REKOMENDASI AI
# ==========================================
class RecommendationRequest(BaseModel):
    prompt: str