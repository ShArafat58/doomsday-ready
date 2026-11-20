from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import BookingQuote, CinemaCreate, CinemaRead
from app.services import cinemas as cinema_service
router = APIRouter(prefix="/api/cinemas", tags=["cinemas"])
@router.get("", response_model=list[CinemaRead])
def list_cinemas(db: Session = Depends(get_db)):
    return [cinema_service.to_read(c) for c in cinema_service.list_cinemas(db)]
@router.post("", response_model=CinemaRead, status_code=status.HTTP_201_CREATED)
def create_cinema(payload: CinemaCreate, db: Session = Depends(get_db)):
    return cinema_service.to_read(cinema_service.create_cinema(db, payload))
@router.get("/{cinema_id}", response_model=CinemaRead)
def get_cinema(cinema_id: int, db: Session = Depends(get_db)):
    return cinema_service.to_read(cinema_service.get_cinema(db, cinema_id))
@router.get("/{cinema_id}/booking", response_model=BookingQuote)
def booking_quote(
    cinema_id: int,
    group_size: int = Query(alias="groupSize", ge=1, le=10000),
    db: Session = Depends(get_db),
):
    return cinema_service.get_booking_quote(db, cinema_id, group_size)
