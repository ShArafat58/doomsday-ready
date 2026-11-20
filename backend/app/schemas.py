from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel
class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        str_strip_whitespace=True,
    )
# Movies
class MovieCreate(CamelModel):
    title: str = Field(min_length=1, max_length=200)
    release_year: int = Field(ge=1900, le=2100)
    runtime_minutes: int = Field(ge=1, le=300)
    prerequisite_ids: list[int] = Field(default_factory=list)
    watched: bool = False
class MovieUpdate(CamelModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    release_year: int | None = Field(default=None, ge=1900, le=2100)
    runtime_minutes: int | None = Field(default=None, ge=1, le=300)
    prerequisite_ids: list[int] | None = None
    watched: bool | None = None
class MovieRead(CamelModel):
    id: int
    title: str
    release_year: int
    runtime_minutes: int
    watched: bool
    prerequisite_ids: list[int]
# Rewatch plan
class RewatchPlan(CamelModel):
    target: MovieRead
    movies: list[MovieRead]
    total_count: int
    watched_count: int
    unwatched_runtime_minutes: int
# Cinemas
BundleSize = Annotated[int, Field(ge=1, le=500)]
class CinemaCreate(CamelModel):
    name: str = Field(min_length=1, max_length=200)
    bundle_sizes: list[BundleSize] = Field(min_length=1, max_length=10)
    @field_validator("bundle_sizes")
    @classmethod
    def sizes_must_be_different(cls, sizes: list[int]) -> list[int]:
        if len(set(sizes)) != len(sizes):
            raise ValueError("bundle sizes must all be different")
        return sorted(sizes)
class CinemaRead(CamelModel):
    id: int
    name: str
    bundle_sizes: list[int]
# Booking
class BookingLine(CamelModel):
    size: int
    count: int
class BookingQuote(CamelModel):
    cinema_id: int
    group_size: int
    possible: bool
    total_bundles: int | None
    bundles: list[BookingLine]
    message: str
