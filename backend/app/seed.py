import sys
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from app import models  # noqa: F401  (import registers the tables)
from app.database import Base, SessionLocal, engine
from app.models import Cinema, CinemaBundleSize, Movie
# Sample data from the task (descriptions written in our own words)
MOVIES = [
    (
        "Iron Man", 2008, 126, [],
        "Captured by terrorists, billionaire inventor Tony Stark builds a suit of armor to escape. "
        "Back home, he upgrades it and becomes Iron Man to fight the weapons his own company made.",
    ),
    (
        "Captain America: The First Avenger", 2011, 124, [],
        "During World War II, a small but brave Steve Rogers becomes a super soldier and leads "
        "the fight against the Red Skull and his secret army, HYDRA.",
    ),
    (
        "The Avengers", 2012, 143, ["Iron Man", "Captain America: The First Avenger"],
        "When Loki arrives with an alien army to take over Earth, Nick Fury brings six very "
        "different heroes together to fight as one team.",
    ),
    (
        "Captain America: Civil War", 2016, 147, ["The Avengers"],
        "A new law to control superheroes splits the Avengers in two, with Captain America and "
        "Iron Man leading opposite sides in a fight that turns personal.",
    ),
    (
        "Thor: Ragnarok", 2017, 130, [],
        "Trapped on a junk planet without his hammer, Thor must survive a gladiator fight against "
        "an old friend and race home to stop Hela from destroying Asgard.",
    ),
    (
        "Avengers: Infinity War", 2018, 149, ["Captain America: Civil War", "Thor: Ragnarok"],
        "Thanos hunts the six Infinity Stones to wipe out half of all life, and the Avengers and "
        "their allies make a desperate stand to stop him.",
    ),
    (
        "Avengers: Endgame", 2019, 181, ["Avengers: Infinity War"],
        "After Thanos wins, the remaining Avengers get one last chance to undo the damage, "
        "through a daring trip into the past.",
    ),
    (
        "Avengers: Doomsday", 2026, 150, ["Avengers: Endgame"],
        "Doctor Doom rises as the next great threat to the heroes. The full story is still a "
        "secret before the premiere.",
    ),
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
    for title, year, runtime, prerequisites, description in MOVIES:
        movie = Movie(
            title=title,
            release_year=year,
            runtime_minutes=runtime,
            description=description,
            prerequisites=[by_title[p] for p in prerequisites],
        )
        db.add(movie)
        by_title[title] = movie
    for name, sizes in CINEMAS:
        db.add(Cinema(name=name, bundle_sizes=[CinemaBundleSize(size=s) for s in sizes]))
    db.commit()
def seed(only_if_empty: bool = False) -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if only_if_empty and db.scalar(select(func.count()).select_from(Movie)):
            print("Database already has data, skipping seed.")
            return
        load_sample_data(db)
    print(f"Seeded {len(MOVIES)} movies and {len(CINEMAS)} cinemas.")
if __name__ == "__main__":
    seed(only_if_empty="--if-empty" in sys.argv)
