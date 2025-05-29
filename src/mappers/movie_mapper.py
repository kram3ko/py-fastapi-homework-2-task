from typing import Dict, Any, List

from database.models import MovieModel
from schemas.movies import MovieDetailResponseSchema


class MovieMapper:
    @staticmethod
    def to_detail_response(movie: MovieModel) -> MovieDetailResponseSchema:
        movie_dict = {
            "id": movie.id,
            "name": movie.name,
            "date": movie.date,
            "score": movie.score,
            "overview": movie.overview,
            "status": movie.status,
            "budget": movie.budget,
            "revenue": movie.revenue,
            "country": {
                "id": movie.country.id,
                "code": movie.country.code,
                "name": movie.country.name,
            }
            if movie.country
            else None,
            "genres": [{"id": genre.id, "name": genre.name} for genre in movie.genres]
            if movie.genres
            else [],
            "actors": [{"id": actor.id, "name": actor.name} for actor in movie.actors]
            if movie.actors
            else [],
            "languages": [{"id": lang.id, "name": lang.name} for lang in movie.languages]
            if movie.languages
            else [],
        }
        return MovieDetailResponseSchema.model_validate(movie_dict)

    @staticmethod
    def to_list_item(movie: MovieModel) -> Dict[str, Any]:
        return {
            "id": movie.id,
            "name": movie.name,
            "date": movie.date,
            "score": movie.score,
            "overview": movie.overview,
        }

    @staticmethod
    def to_list_items(movies: List[MovieModel]) -> List[Dict[str, Any]]:
        return [MovieMapper.to_list_item(movie) for movie in movies]
