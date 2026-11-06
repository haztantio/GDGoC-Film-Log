from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    created_time = Column(DateTime, default=datetime.utcnow)

    # Relasi balik untuk mempermudah pemanggilan data
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("WatchedReview", back_populates="user", cascade="all, delete-orphan")

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    year = Column(Integer)
    director = Column(String)
    genres = Column(String)
    rating = Column(Float)
    duration = Column(String)
    synopsis = Column(Text)
    poster_url = Column(String)
    cast = Column(Text)

    watchlists = relationship("Watchlist", back_populates="movie", cascade="all, delete-orphan")
    reviews = relationship("WatchedReview", back_populates="movie", cascade="all, delete-orphan")

class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    added_time = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlists")
    movie = relationship("Movie", back_populates="watchlists")

    # Mencegah pengguna memasukkan film yang sama berkali-kali
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='_user_movie_uc'),)

class WatchedReview(Base):
    __tablename__ = "watched_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    review = Column(Text)
    watched_time = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    movie = relationship("Movie", back_populates="reviews")

