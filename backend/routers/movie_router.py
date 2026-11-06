from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
import os
from .. import models, schemas, dependencies
from ..database import get_db
import google.generativeai as genai
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from ..services.ai_service import generate_movie_recommendation
from datetime import datetime

# Menarik kunci rahasia dari file .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Membuat router khusus untuk urusan katalog film
router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)

# ==========================================
# 1. Endpoint SEEDING (Memasukkan 20 film dari JSON ke Database)
# ==========================================
@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_movies(db: Session = Depends(get_db)):
    # 1. Cek dulu apakah database sudah berisi film. 
    # Ini penting agar kita tidak memasukkan data kembar jika tombol terpencet 2 kali.
    existing_movies = db.query(models.Movie).count()
    if existing_movies > 0:
        return {"pesan": f"Database sudah berisi {existing_movies} film. Proses seeding dilewati."}
    
    try:
        # 2. Buka dan baca file movies.json bawaan starter-pack
        # Karena kita menjalankan uvicorn dari folder utama, path-nya adalah 'data/movies.json'
        with open("data/movies.json", "r", encoding="utf-8") as file:
            movies_data = json.load(file)
            
        # 3. Looping: Ubah setiap baris data JSON menjadi objek database SQLAlchemy
        for item in movies_data:
            new_movie = models.Movie(
                title=item.get("title"),
                year=item.get("year"),
                director=item.get("director"),
                genres=item.get("genres"),
                rating=item.get("rating"),
                duration=item.get("duration"),
                synopsis=item.get("synopsis"),
                poster_url=item.get("poster_url"),
                cast=item.get("cast")
            )
            db.add(new_movie) # Kumpulkan ke keranjang belanja
            
        # 4. Simpan semua isi keranjang ke PostgreSQL secara permanen (Commit)
        db.commit()
        return {"pesan": "Berhasil! 20 film awal telah disuntikkan ke dalam database."}
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File movies.json tidak ditemukan di folder data/")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan sistem: {str(e)}")

# ==========================================
# 2. Endpoint GET MOVIES (Menampilkan seluruh katalog film)
# ==========================================
@router.get("/", response_model=list[schemas.MovieResponse])
def get_all_movies(db: Session = Depends(get_db)):
    """Mengambil semua daftar film dari database untuk ditampilkan ke Frontend"""
    movies = db.query(models.Movie).all()
    return movies

# ==========================================
# 4. REKOMENDASI FILM DENGAN GEMINI AI (Grounding System)
# ==========================================
@router.post("/recommend")
def get_ai_recommendation(
    request: schemas.RecommendationRequest, 
    db: Session = Depends(get_db)
):
    movies = db.query(models.Movie).all()
    if not movies:
        raise HTTPException(status_code=404, detail="Database film kosong.")

    # Siapkan katalog string
    movie_catalog = "".join([f"ID: {m.id} | Judul: {m.title} | Genre: {m.genres} | Sinopsis: {m.synopsis}\n" for m in movies])

    # Panggil service AI yang baru dibuat
    try:
        ai_result = generate_movie_recommendation(request.prompt, movie_catalog)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saat menghubungi Gemini: {str(e)}")

    # Cari film hasil rekomendasi di database
    recommended_movie = db.query(models.Movie).filter(models.Movie.id == ai_result.get("movie_id")).first()

    if not recommended_movie:
        recommended_movie = movies[0]
        ai_result["reasoning"] = "Pilihan default (AI mencoba merekomendasikan di luar konteks database)."

    return {
        "movie_id": recommended_movie.id,
        "reasoning": ai_result["reasoning"],
        "movie": recommended_movie
    }

# ==========================================
# 3. MENDAPATKAN DETAIL SATU FILM (Sesuai Kontrak GDGoC)
# ==========================================
@router.get("/{movie_id}", response_model=schemas.MovieResponse)
def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    """Mengambil detail satu film spesifik berdasarkan ID"""
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan")
        
    return movie

# 1. Rute Menyimpan/Memperbarui Ulasan
@router.post("/watched", response_model=schemas.WatchedResponse)
def add_watched_log(
    watched_data: schemas.WatchedCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    # Cek apakah film ini sudah pernah diberi ulasan sebelumnya
    existing_log = db.query(models.WatchedReview).filter(
        models.WatchedReview.user_id == current_user.id,
        models.WatchedReview.movie_id == watched_data.movie_id
    ).first()

    if existing_log:
        # Jika sudah ada, perbarui bintang dan teksnya
        existing_log.rating = watched_data.rating
        existing_log.review = watched_data.review
        db.commit()
        db.refresh(existing_log)
        return existing_log
    else:
        # Jika belum ada, buat entri ulasan baru
        new_log = models.WatchedReview(
            user_id=current_user.id,
            movie_id=watched_data.movie_id,
            rating=watched_data.rating,
            review=watched_data.review
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log

# 2. Rute Menampilkan Daftar Ulasan di Tab "Watched & Reviews"
@router.get("/watched", response_model=list[schemas.WatchedResponse])
def get_watched_log(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    # Sisipkan .options(joinedload(...)) agar data film ikut terangkut
    return db.query(models.WatchedReview).options(
        joinedload(models.WatchedReview.movie)
    ).filter(models.WatchedReview.user_id == current_user.id).all()