from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.algorithms.booking import fewest_bundles
from app.errors import AppError
from app.models import Cinema, CinemaBundleSize
from app.schemas import BookingLine, BookingQuote, CinemaCreate, CinemaRead
# Read helpers
def to_read(cinema: Cinema) -> CinemaRead:
    return CinemaRead(
        id=cinema.id,
        name=cinema.name,
        bundle_sizes=[b.size for b in cinema.bundle_sizes],
    )
def list_cinemas(db: Session) -> list[Cinema]:
    return list(db.scalars(select(Cinema).order_by(Cinema.name)))
def get_cinema(db: Session, cinema_id: int) -> Cinema:
    cinema = db.get(Cinema, cinema_id)
    if cinema is None:
        raise AppError(404, "CINEMA_NOT_FOUND", f"Cinema {cinema_id} does not exist.")
    return cinema
# Create
def create_cinema(db: Session, payload: CinemaCreate) -> Cinema:
    taken = db.scalar(select(Cinema.id).where(func.lower(Cinema.name) == payload.name.lower()))
    if taken is not None:
        raise AppError(409, "NAME_TAKEN", f"A cinema named '{payload.name}' already exists.")
    cinema = Cinema(
        name=payload.name,
        bundle_sizes=[CinemaBundleSize(size=s) for s in payload.bundle_sizes],
    )
    db.add(cinema)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError(409, "NAME_TAKEN", "A cinema with this name already exists.")
    db.refresh(cinema)
    return cinema
# Booking quote
def get_booking_quote(db: Session, cinema_id: int, group_size: int) -> BookingQuote:
    cinema = get_cinema(db, cinema_id)
    counts = fewest_bundles([b.size for b in cinema.bundle_sizes], group_size)
    if counts is None:
        return BookingQuote(
            cinema_id=cinema.id,
            group_size=group_size,
            possible=False,
            total_bundles=None,
            bundles=[],
            message=f"Not possible: no mix of bundles adds up to exactly {group_size} seats.",
        )
    lines = [BookingLine(size=size, count=counts[size]) for size in sorted(counts, reverse=True)]
    total = sum(line.count for line in lines)
    word = "bundle" if total == 1 else "bundles"
    summary = ", ".join(f"{line.size} x {line.count}" for line in lines)
    return BookingQuote(
        cinema_id=cinema.id,
        group_size=group_size,
        possible=True,
        total_bundles=total,
        bundles=lines,
        message=f"{total} {word}: {summary}",
    )
