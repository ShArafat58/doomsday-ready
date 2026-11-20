from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Join table: one row means "movie_id needs prerequisite_id watched first".
movie_prerequisites = Table(
    "movie_prerequisites",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("prerequisite_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    CheckConstraint("movie_id <> prerequisite_id", name="ck_movie_not_own_prerequisite"),
)


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        CheckConstraint("runtime_minutes BETWEEN 1 AND 300", name="ck_movie_runtime_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), unique=True)
    release_year: Mapped[int]
    runtime_minutes: Mapped[int]
    watched: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str | None] = mapped_column(String(500), default=None)

    prerequisites: Mapped[list["Movie"]] = relationship(
        secondary=movie_prerequisites,
        primaryjoin=lambda: Movie.id == movie_prerequisites.c.movie_id,
        secondaryjoin=lambda: Movie.id == movie_prerequisites.c.prerequisite_id,
        lazy="selectin",
    )


class Cinema(Base):
    __tablename__ = "cinemas"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)

    bundle_sizes: Mapped[list["CinemaBundleSize"]] = relationship(
        back_populates="cinema",
        cascade="all, delete-orphan",
        order_by="CinemaBundleSize.size",
        lazy="selectin",
    )


class CinemaBundleSize(Base):
    __tablename__ = "cinema_bundle_sizes"
    __table_args__ = (
        CheckConstraint("size BETWEEN 1 AND 500", name="ck_bundle_size_range"),
    )

    cinema_id: Mapped[int] = mapped_column(
        ForeignKey("cinemas.id", ondelete="CASCADE"), primary_key=True
    )
    size: Mapped[int] = mapped_column(primary_key=True)

    cinema: Mapped[Cinema] = relationship(back_populates="bundle_sizes")
