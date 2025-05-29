from datetime import date as date_type
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from database.models import MovieStatusEnum


class CountryInputSchema(BaseModel):
    code: str


class GenreInputSchema(BaseModel):
    name: str


class ActorInputSchema(BaseModel):
    name: str


class LanguageInputSchema(BaseModel):
    name: str


class CountryDetailSchema(BaseModel):
    id: int
    code: str
    name: str | None

    model_config = ConfigDict(from_attributes=True)


class ActorDetailSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class LanguageDetailSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class GenreDetailSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class MovieBase(BaseModel):
    name: str
    date: date_type
    score: float
    overview: str


class MovieDetailSchema(MovieBase):
    id: int
    status: str
    budget: float
    revenue: float
    country: CountryDetailSchema
    genres: list[GenreDetailSchema]
    actors: list[ActorDetailSchema]
    languages: list[LanguageDetailSchema]

    model_config = ConfigDict(from_attributes=True)


class MovieCreateSchema(MovieBase):
    status: MovieStatusEnum
    budget: float
    revenue: float
    country: str
    genres: list[str]
    actors: list[str]
    languages: list[str]


class MovieUpdateSchema(MovieBase):
    name: str | None = None
    date: date_type | None = None
    score: float | None = None
    overview: str | None = None
    status: MovieStatusEnum | None = None
    budget: float | None = None
    revenue: float | None = None
    country: str | None = None
    genres: list[str] | None = None
    actors: list[str] | None = None
    languages: list[str] | None = None


class MovieListItemSchema(MovieBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


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
    date: date_type
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


class MovieUpdateResponseSchema(MovieDetailResponseSchema):
    detail: str
