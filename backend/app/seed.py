from sqlalchemy import text
from app import models  # noqa: F401  (import registers the tables)
from app.database import Base, SessionLocal, engine
from app.models import Movie
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
def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(text("TRUNCATE movie_prerequisites, movies RESTART IDENTITY CASCADE"))
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
        db.commit()
    print(f"Seeded {len(MOVIES)} movies.")
if __name__ == "__main__":
    seed()
