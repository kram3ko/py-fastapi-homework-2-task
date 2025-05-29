from typing import List, Optional, Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import (
    MovieModel,
    CountryModel,
    GenreModel,
    ActorModel,
    LanguageModel
)
from mappers.movie_mapper import MovieMapper
from schemas.movies import MovieCreateSchema, MovieUpdateSchema


class MovieService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_movies(self, page: int, per_page: int) -> Dict[str, Any]:
        count_stmt = select(func.count(MovieModel.id))
        result = await self.db.execute(count_stmt)
        total = result.scalar_one()

        if total == 0:
            return None

        max_page = (total + per_page - 1) // per_page
        if page > max_page:
            return None

        offset = (page - 1) * per_page
        stmt = (
            select(MovieModel)
            .order_by(MovieModel.id.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await self.db.execute(stmt)
        movies = result.scalars().all()

        base_path = "/theater/movies/"
        next_page = (
            f"{base_path}?page={page + 1}&per_page={per_page}" if page < max_page else None
        )
        prev_page = f"{base_path}?page={page - 1}&per_page={per_page}" if page > 1 else None

        return {
            "movies": MovieMapper.to_list_items(movies),
            "prev_page": prev_page,
            "next_page": next_page,
            "total_pages": max_page,
            "total_items": total,
        }

    async def get_movie_by_id(self, movie_id: int) -> Optional[MovieModel]:
        stmt = (
            select(MovieModel)
            .options(
                joinedload(MovieModel.country),
                joinedload(MovieModel.genres),
                joinedload(MovieModel.actors),
                joinedload(MovieModel.languages),
            )
            .where(MovieModel.id == movie_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_movie(self, movie_data: MovieCreateSchema) -> Optional[MovieModel]:
        stmt = select(MovieModel).where(
            and_(MovieModel.name == movie_data.name, MovieModel.date == movie_data.date)
        )
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            return None

        country = await self._get_or_create_country(movie_data.country)

        genres = await self._get_or_create_genres(movie_data.genres)

        actors = await self._get_or_create_actors(movie_data.actors)

        languages = await self._get_or_create_languages(movie_data.languages)

        movie_dict = movie_data.model_dump(
            exclude={"country", "genres", "actors", "languages"}
        )
        new_movie = MovieModel(
            **movie_dict,
            country=country,
            genres=genres,
            actors=actors,
            languages=languages
        )
        self.db.add(new_movie)
        await self.db.commit()
        await self.db.refresh(new_movie)

        return await self.get_movie_by_id(new_movie.id)

    async def update_movie(self, movie_id: int, movie_data: MovieUpdateSchema) -> Optional[MovieModel]:
        movie = await self.get_movie_by_id(movie_id)
        if not movie:
            return None

        update_data = movie_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field not in {"country", "genres", "actors", "languages"}:
                setattr(movie, field, value)

        if "country" in update_data:
            movie.country = await self._get_or_create_country(update_data["country"])

        if "genres" in update_data:
            movie.genres = await self._get_or_create_genres(update_data["genres"])

        if "actors" in update_data:
            movie.actors = await self._get_or_create_actors(update_data["actors"])

        if "languages" in update_data:
            movie.languages = await self._get_or_create_languages(update_data["languages"])

        await self.db.commit()
        await self.db.refresh(movie)
        return movie

    async def delete_movie(self, movie_id: int) -> bool:
        movie = await self.get_movie_by_id(movie_id)
        if not movie:
            return False

        await self.db.delete(movie)
        await self.db.commit()
        return True

    async def _get_or_create_country(self, code: str) -> CountryModel:
        country_stmt = select(CountryModel).where(CountryModel.code == code)
        country_result = await self.db.execute(country_stmt)
        country = country_result.scalar_one_or_none()
        if not country:
            country = CountryModel(code=code, name=code)
            self.db.add(country)
            await self.db.flush()
        return country

    async def _get_or_create_genres(self, genre_names: List[str]) -> List[GenreModel]:
        genres = []
        for genre_name in genre_names:
            genre_stmt = select(GenreModel).where(GenreModel.name == genre_name)
            genre_result = await self.db.execute(genre_stmt)
            genre = genre_result.scalar_one_or_none()
            if not genre:
                genre = GenreModel(name=genre_name)
                self.db.add(genre)
                await self.db.flush()
            genres.append(genre)
        return genres

    async def _get_or_create_actors(self, actor_names: List[str]) -> List[ActorModel]:
        actors = []
        for actor_name in actor_names:
            actor_stmt = select(ActorModel).where(ActorModel.name == actor_name)
            actor_result = await self.db.execute(actor_stmt)
            actor = actor_result.scalar_one_or_none()
            if not actor:
                actor = ActorModel(name=actor_name)
                self.db.add(actor)
                await self.db.flush()
            actors.append(actor)
        return actors

    async def _get_or_create_languages(self, language_names: List[str]) -> List[LanguageModel]:
        languages = []
        for lang_name in language_names:
            lang_stmt = select(LanguageModel).where(LanguageModel.name == lang_name)
            lang_result = await self.db.execute(lang_stmt)
            language = lang_result.scalar_one_or_none()
            if not language:
                language = LanguageModel(name=lang_name)
                self.db.add(language)
                await self.db.flush()
            languages.append(language)
        return languages
