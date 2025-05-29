from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseMovieSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., max_length=255)
    date: date
    score: float = Field(..., ge=0, le=100)
    overview: str
    status: str
    budget: float = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    country: str | None
    genres: list[str]
    actors: list[str]
    languages: list[str]

    @field_validator("date")
    @classmethod
    def validate_date(cls, value):
        if value > date.today().replace(year=date.today().year + 1):
            raise ValueError("Date cannot be more than one year in the future")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        valid_statuses = ["Released", "Post Production", "In Production"]
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value


class MovieListItemSchema(BaseModel):
    id: int
    name: str
    date: date
    score: float
    overview: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 9936,
                    "name": "Avatar new",
                    "date": "2022-12-15",
                    "score": 78.0,
                    "overview": "Set more than a decade after the events of the first film...",
                }
            ]
        },
    )


class MovieListResponseSchema(BaseModel):
    movies: list[MovieListItemSchema]
    prev_page: str | None
    next_page: str | None
    total_pages: int
    total_items: int

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "movies": [
                        {
                            "id": 9936,
                            "name": "Avatar new",
                            "date": "2022-12-15",
                            "score": 78.0,
                            "overview": "Set more than a decade after the events of the first film...",
                        }
                    ],
                    "prev_page": None,
                    "next_page": "/theater/movies/?page=2&per_page=1",
                    "total_pages": 9934,
                    "total_items": 9934,
                }
            ]
        }
    )


class CountrySchema(BaseModel):
    id: int
    code: str
    name: str | None


class GenreSchema(BaseModel):
    id: int
    name: str


class ActorSchema(BaseModel):
    id: int
    name: str


class LanguageSchema(BaseModel):
    id: int
    name: str


class MovieDetailResponseSchema(BaseModel):
    id: int
    name: str
    date: date
    score: float
    overview: str
    status: str
    budget: float
    revenue: float
    country: CountrySchema | None
    genres: list[GenreSchema]
    actors: list[ActorSchema]
    languages: list[LanguageSchema]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Creed III",
                    "date": "2023-03-02",
                    "score": 73,
                    "genres": [
                        {"id": 7, "name": "Drama"},
                        {"id": 12, "name": "Action"},
                    ],
                    "overview": "After dominating the boxing world,"
                                " Adonis Creed has been thriving in both "
                                "his career and family life...",
                    "actors": [
                        {"id": 1, "name": "Michael B. Jordan"},
                        {"id": 2, "name": "Tessa Thompson"},
                    ],
                    "languages": [{"id": 1, "name": "English"}],
                    "status": "Released",
                    "budget": 75000000,
                    "revenue": 271616668,
                    "country": {"id": 1, "code": "AU", "name": "Australia"},
                }
            ]
        }
    )


class MovieCreateSchema(BaseModel):
    name: str = Field(..., max_length=255)
    date: date
    score: float = Field(..., ge=0, le=100)
    overview: str
    status: str
    budget: float = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    country: str
    genres: list[str]
    actors: list[str]
    languages: list[str]

    @field_validator("date")
    @classmethod
    def validate_date(cls, value):
        if value > date.today().replace(year=date.today().year + 1):
            raise ValueError("Date cannot be more than one year in the future")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        valid_statuses = ["Released", "Post Production", "In Production"]
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value


class MovieUpdateSchema(BaseModel):
    name: str | None = Field(None, max_length=255)
    date: Optional[date] = None
    score: float | None = Field(None, ge=0, le=100)
    overview: str | None = None
    status: str | None = None
    budget: float | None = Field(None, ge=0)
    revenue: float | None = Field(None, ge=0)
    country: str | None = None
    genres: list[str] | None = None
    actors: list[str] | None = None
    languages: list[str] | None = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, value):
        if value and value > date.today().replace(year=date.today().year + 1):
            raise ValueError("Date cannot be more than one year in the future")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value:
            valid_statuses = ["Released", "Post Production", "In Production"]
            if value not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
