from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MovieCreate, MovieRead, MovieUpdate
from app.services import movies as movie_service

router = APIRouter(prefix="/api/movies", tags=["movies"])


@router.get("", response_model=list[MovieRead])
def list_movies(db: Session = Depends(get_db)):
    return [movie_service.to_read(m) for m in movie_service.list_movies(db)]


@router.post("", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
def create_movie(payload: MovieCreate, db: Session = Depends(get_db)):
    return movie_service.to_read(movie_service.create_movie(db, payload))


@router.get("/{movie_id}", response_model=MovieRead)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    return movie_service.to_read(movie_service.get_movie(db, movie_id))


@router.patch("/{movie_id}", response_model=MovieRead)
def update_movie(movie_id: int, payload: MovieUpdate, db: Session = Depends(get_db)):
    return movie_service.to_read(movie_service.update_movie(db, movie_id, payload))
