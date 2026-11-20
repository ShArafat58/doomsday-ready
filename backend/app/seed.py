from sqlalchemy import text
from sqlalchemy.orm import Session
from app import models  # noqa: F401  (import registers the tables)
from app.database import Base, SessionLocal, engine
from app.models import Cinema, CinemaBundleSize, Movie
# Sample data from the task
MOVIES = [
    ("Iron Man", 2008, 126, []),
    ("Captain America: The First Avenger", 2011, 124, []),
    ("The Avengers", 2012, 143, ["Iron Man", "Captain America: The First Avenger"]),
    ("Captain America: Civil War", 2016, 147, ["The Avengers"]),
    ("Thor: Ragnarok", 2017, 130, []),
    ("Avengers: Infinity War", 2018, 149, ["Captain America: Civil War", "Thor: Ragnarok"]),
    ("Avengers: Endgame", 2019, 181, ["Avengers: Infinity War"]),
    ("Avengers: Doomsday", 2026, 150, ["Avengers: Endgame"]),
]
CINEMAS = [
    ("Starlight Cinema", [1, 3, 4]),
    ("Nebula Screens", [2, 5]),
    ("Quantum Theatre", [6, 9, 20]),
    ("Orbit Hall", [4, 6]),
]
def load_sample_data(db: Session) -> None:
    db.execute(text(
        "TRUNCATE movie_prerequisites, movies, cinema_bundle_sizes, cinemas "
        "RESTART IDENTITY CASCADE"
    ))
    by_title: dict[str, Movie] = {}
    for title, year, runtime, prerequisites in MOVIES:
        movie = Movie(
            title=title,
            release_year=year,
            runtime_minutes=runtime,
            prerequisites=[by_title[p] for p in prerequisites],
        )
        db.add(movie)
        by_title[title] = movie
    for name, sizes in CINEMAS:
        db.add(Cinema(name=name, bundle_sizes=[CinemaBundleSize(size=s) for s in sizes]))
    db.commit()
def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        load_sample_data(db)
    print(f"Seeded {len(MOVIES)} movies and {len(CINEMAS)} cinemas.")
if __name__ == "__main__":
    seed()
