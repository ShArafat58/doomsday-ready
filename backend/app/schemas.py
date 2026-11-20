from pydantic import BaseModel, ConfigDict, Field
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
