from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user

# 1. HANYA GUNAKAN SATU ROUTER UTAMA (Tanpa Prefix agar tidak ada masalah trailing slash)
router = APIRouter(
    tags=["Watchlist & Watched"]
)

# ==========================================
# 1. WATCHLIST ENDPOINTS (Daftar Tontonan Nanti)
# ==========================================
@router.post("/watchlist", response_model=schemas.WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_watchlist(
    data: schemas.WatchlistCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Menambahkan film ke watchlist pengguna (Mencegah Duplikasi)"""
    movie_exists = db.query(models.Movie).filter(models.Movie.id == data.movie_id).first()
    if not movie_exists:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan di database")

    existing = db.query(models.Watchlist).filter(
        models.Watchlist.user_id == current_user.id,
        models.Watchlist.movie_id == data.movie_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="Film ini sudah ada di Watchlist kamu")

    new_item = models.Watchlist(user_id=current_user.id, movie_id=data.movie_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/watchlist", response_model=list[schemas.WatchlistResponse])
def get_my_watchlist(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Melihat isi watchlist milik user yang sedang login"""
    return db.query(models.Watchlist).filter(models.Watchlist.user_id == current_user.id).all()


@router.delete("/watchlist/{movie_id}")
def remove_from_watchlist(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Menghapus film dari watchlist"""
    item = db.query(models.Watchlist).filter(
        models.Watchlist.user_id == current_user.id,
        models.Watchlist.movie_id == movie_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan di watchlist kamu")

    db.delete(item)
    db.commit()
    return {"pesan": "Film berhasil dihapus dari watchlist"}


# ==========================================
# 2. WATCHED ENDPOINTS (Riwayat Tontonan & Ulasan)
# ==========================================

@router.post("/watched", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def add_watched_log(
    data: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Mencatat film yang sudah ditonton beserta rating (1-5) dan ulasan (Mencegah Duplikasi)"""
    movie_exists = db.query(models.Movie).filter(models.Movie.id == data.movie_id).first()
    if not movie_exists:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan")

    # Hapus dari watchlist jika ada
    watchlist_item = db.query(models.Watchlist).filter(
        models.Watchlist.user_id == current_user.id,
        models.Watchlist.movie_id == data.movie_id
    ).first()
    if watchlist_item:
        db.delete(watchlist_item)

    # -------------------------------------------------
    # LOGIKA PEMBASMI DUPLIKAT (UPSERT)
    # -------------------------------------------------
    existing_logs = db.query(models.WatchedReview).filter(
        models.WatchedReview.user_id == current_user.id,
        models.WatchedReview.movie_id == data.movie_id
    ).all()

    if existing_logs:
        # Jika sudah ada, TIMPA data pertama (Update)
        main_log = existing_logs[0]
        main_log.rating = data.rating
        main_log.review = data.review
        
        # HAPUS sisa duplikat hantu (Auto-Clean)
        if len(existing_logs) > 1:
            for extra_log in existing_logs[1:]:
                db.delete(extra_log)
        
        db.commit()
        db.refresh(main_log)
        return main_log
    else:
        # Jika benar-benar baru, buat baris baru (Insert)
        new_review = models.WatchedReview(
            user_id=current_user.id,
            movie_id=data.movie_id,
            rating=data.rating,
            review=data.review
        )
        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        return new_review


@router.get("/watched", response_model=list[schemas.ReviewResponse])
def get_my_watched_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Melihat riwayat film yang sudah ditonton (khusus user ini)"""
    return db.query(models.WatchedReview).filter(models.WatchedReview.user_id == current_user.id).all()