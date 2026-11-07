from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Bagian data model untuk req dan response API
# Skema JWT Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Skema user register, login, dan response user
class UserCreate(BaseModel):
    email: EmailStr  
    password: str 
    username: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_time: datetime

    model_config = {"from_attributes": True} 

# Skema Movie response 
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

class WatchedCreate(BaseModel):
    movie_id: int
    rating: int
    review: str | None = None

class WatchedResponse(BaseModel):
    id: int
    movie_id: int
    rating: int
    review: str | None = None  
    watched_time: datetime | None = None  
    movie: MovieResponse

    class Config:
        from_attributes = True

# Skema watchlist
class WatchlistCreate(BaseModel):
    movie_id: int

class WatchlistResponse(BaseModel):
    id: int
    movie_id: int
    added_time: datetime
    movie: MovieResponse 

    model_config = {"from_attributes": True}

# Skema reviewss
class ReviewCreate(BaseModel):
    movie_id: int
    rating: int = Field(..., ge=1, le=5) 
    review: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    movie_id: int
    rating: int
    review: Optional[str]
    watched_time: datetime
    movie: MovieResponse

    model_config = {"from_attributes": True}

# Skema rekomendasi AI
class RecommendationRequest(BaseModel):
    prompt: str