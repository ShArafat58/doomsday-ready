from pydantic.alias_generators import to_camel
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.algorithms.graph import Graph, find_cycle
from app.errors import AppError
from app.models import Movie, movie_prerequisites
from app.schemas import MovieCreate, MovieRead, MovieUpdate


# Read helpers

def to_read(movie: Movie) -> MovieRead:
    return MovieRead(
        id=movie.id,
        title=movie.title,
        release_year=movie.release_year,
        runtime_minutes=movie.runtime_minutes,
        watched=movie.watched,
        description=movie.description,
        prerequisite_ids=sorted(p.id for p in movie.prerequisites),
    )


def list_movies(db: Session) -> list[Movie]:
    return list(db.scalars(select(Movie).order_by(Movie.release_year, Movie.title)))


def get_movie(db: Session, movie_id: int) -> Movie:
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise AppError(404, "MOVIE_NOT_FOUND", f"Movie {movie_id} does not exist.")
    return movie


def load_graph(db: Session) -> Graph:
    graph: Graph = {}
    rows = db.execute(select(movie_prerequisites.c.movie_id, movie_prerequisites.c.prerequisite_id))
    for movie_id, prerequisite_id in rows:
        graph.setdefault(movie_id, []).append(prerequisite_id)
    return graph


# Validation

def _ensure_title_free(db: Session, title: str, exclude_id: int | None = None) -> None:
    stmt = select(Movie.id).where(func.lower(Movie.title) == title.lower())
    if exclude_id is not None:
        stmt = stmt.where(Movie.id != exclude_id)
    if db.scalar(stmt) is not None:
        raise AppError(409, "TITLE_TAKEN", f"A movie titled '{title}' already exists.")


def _load_prerequisites(db: Session, ids: list[int]) -> list[Movie]:
    unique_ids = list(dict.fromkeys(ids))
    if not unique_ids:
        return []
    found = {m.id: m for m in db.scalars(select(Movie).where(Movie.id.in_(unique_ids)))}
    missing = [i for i in unique_ids if i not in found]
    if missing:
        raise AppError(
            422,
            "PREREQUISITE_NOT_FOUND",
            f"These prerequisite ids do not exist: {missing}.",
            {"missingIds": missing},
        )
    return [found[i] for i in unique_ids]


def _ensure_no_cycle(db: Session, movie: Movie, prerequisites: list[Movie]) -> None:
    path = find_cycle(load_graph(db), movie.id, [p.id for p in prerequisites])
    if path is None:
        return
    titles = {m.id: m.title for m in db.scalars(select(Movie).where(Movie.id.in_(path)))}
    names = [titles[i] for i in path]
    raise AppError(
        409,
        "CIRCULAR_DEPENDENCY",
        "This change would make a movie depend on itself: " + " -> ".join(names),
        {"cycle": names},
    )


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError(409, "TITLE_TAKEN", "A movie with this title already exists.")


# Create and update

def create_movie(db: Session, payload: MovieCreate) -> Movie:
    _ensure_title_free(db, payload.title)
    prerequisites = _load_prerequisites(db, payload.prerequisite_ids)

    movie = Movie(
        title=payload.title,
        release_year=payload.release_year,
        runtime_minutes=payload.runtime_minutes,
        watched=payload.watched,
        description=payload.description,
        prerequisites=prerequisites,
    )
    db.add(movie)
    _commit(db)
    db.refresh(movie)
    return movie


def update_movie(db: Session, movie_id: int, payload: MovieUpdate) -> Movie:
    movie = get_movie(db, movie_id)
    changes = payload.model_dump(exclude_unset=True)

    null_fields = [to_camel(name) for name, value in changes.items() if value is None and name != "description"]
    if null_fields:
        raise AppError(422, "VALIDATION_ERROR", f"These fields cannot be null: {null_fields}.")

    if "title" in changes:
        _ensure_title_free(db, changes["title"], exclude_id=movie.id)

    new_prerequisites = None
    if "prerequisite_ids" in changes:
        new_prerequisites = _load_prerequisites(db, changes["prerequisite_ids"])
        _ensure_no_cycle(db, movie, new_prerequisites)

    for field in ("title", "release_year", "runtime_minutes", "watched", "description"):
        if field in changes:
            setattr(movie, field, changes[field])
    if new_prerequisites is not None:
        movie.prerequisites = new_prerequisites

    _commit(db)
    db.refresh(movie)
    return movie
