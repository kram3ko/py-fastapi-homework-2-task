from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_db, MovieModel
from database.models import GenreModel, ActorModel, LanguageModel, CountryModel
from schemas import MovieListResponseSchema
from schemas.movies import (
    MovieDetailResponseSchema,
    MovieCreateSchema,
    MovieUpdateSchema,
)

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    count_stmt = select(func.count(MovieModel.id))
    result = await db.execute(count_stmt)
    total = result.scalar_one()

    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No movies found."
        )

    max_page = (total + per_page - 1) // per_page
    if page > max_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page {page} exceeds maximum available page {max_page}.",
        )

    offset = (page - 1) * per_page
    stmt = (
        select(MovieModel).order_by(MovieModel.id.desc()).offset(offset).limit(per_page)
    )
    result = await db.execute(stmt)
    movies = result.scalars().all()

    movie_items = [
        {
            "id": movie.id,
            "name": movie.name,
            "date": movie.date,
            "score": movie.score,
            "overview": movie.overview,
        }
        for movie in movies
    ]

    base_path = "/theater/movies/"
    next_page = (
        f"{base_path}?page={page + 1}&per_page={per_page}" if page < max_page else None
    )
    prev_page = f"{base_path}?page={page - 1}&per_page={per_page}" if page > 1 else None

    return {
        "movies": movie_items,
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": max_page,
        "total_items": total,
    }


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
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
    result = await db.execute(stmt)
    movie = result.unique().scalar_one_or_none()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found.",
        )

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


@router.post(
    "/movies/",
    response_model=MovieDetailResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_movie(
    movie_data: MovieCreateSchema, db: AsyncSession = Depends(get_db)
):
    stmt = select(MovieModel).where(
        and_(MovieModel.name == movie_data.name, MovieModel.date == movie_data.date)
    )
    result = await db.execute(stmt)
    existing_movie = result.scalar_one_or_none()
    if existing_movie:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A movie with the name '{movie_data.name}' and release date '{movie_data.date}' already exists.",
        )

    country_stmt = select(CountryModel).where(CountryModel.code == movie_data.country)
    country_result = await db.execute(country_stmt)
    country = country_result.scalar_one_or_none()
    if not country:
        country = CountryModel(code=movie_data.country, name=movie_data.country)
        db.add(country)
        await db.flush()

    genres = []
    for genre_name in movie_data.genres:
        genre_stmt = select(GenreModel).where(GenreModel.name == genre_name)
        genre_result = await db.execute(genre_stmt)
        genre = genre_result.scalar_one_or_none()
        if not genre:
            genre = GenreModel(name=genre_name)
            db.add(genre)
            await db.flush()
        genres.append(genre)

    actors = []
    for actor_name in movie_data.actors:
        actor_stmt = select(ActorModel).where(ActorModel.name == actor_name)
        actor_result = await db.execute(actor_stmt)
        actor = actor_result.scalar_one_or_none()
        if not actor:
            actor = ActorModel(name=actor_name)
            db.add(actor)
            await db.flush()
        actors.append(actor)

    languages = []
    for lang_name in movie_data.languages:
        lang_stmt = select(LanguageModel).where(LanguageModel.name == lang_name)
        lang_result = await db.execute(lang_stmt)
        language = lang_result.scalar_one_or_none()
        if not language:
            language = LanguageModel(name=lang_name)
            db.add(language)
            await db.flush()
        languages.append(language)

    movie_dict = movie_data.model_dump(
        exclude={"country", "genres", "actors", "languages"}
    )
    new_movie = MovieModel(
        **movie_dict, country=country, genres=genres, actors=actors, languages=languages
    )
    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)

    stmt = (
        select(MovieModel)
        .options(
            joinedload(MovieModel.country),
            joinedload(MovieModel.genres),
            joinedload(MovieModel.actors),
            joinedload(MovieModel.languages),
        )
        .where(MovieModel.id == new_movie.id)
    )
    result = await db.execute(stmt)
    new_movie = result.unique().scalar_one()

    movie_dict = {
        "id": new_movie.id,
        "name": new_movie.name,
        "date": new_movie.date,
        "score": new_movie.score,
        "overview": new_movie.overview,
        "status": new_movie.status,
        "budget": new_movie.budget,
        "revenue": new_movie.revenue,
        "country": {
            "id": new_movie.country.id,
            "code": new_movie.country.code,
            "name": new_movie.country.name,
        }
        if new_movie.country
        else None,
        "genres": [{"id": genre.id, "name": genre.name} for genre in new_movie.genres]
        if new_movie.genres
        else [],
        "actors": [{"id": actor.id, "name": actor.name} for actor in new_movie.actors]
        if new_movie.actors
        else [],
        "languages": [
            {"id": lang.id, "name": lang.name} for lang in new_movie.languages
        ]
        if new_movie.languages
        else [],
    }

    return MovieDetailResponseSchema.model_validate(movie_dict)


@router.delete("/movies/{movie_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await db.scalar(select(MovieModel).where(MovieModel.id == movie_id))

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found.",
        )

    await db.delete(movie)
    await db.commit()


@router.patch("/movies/{movie_id}/")
async def update_movie(
    movie_id: int, movie_data: MovieUpdateSchema, db: AsyncSession = Depends(get_db)
):
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
    result = await db.execute(stmt)
    movie = result.unique().scalar_one_or_none()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found.",
        )

    update_data = movie_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field not in {"country", "genres", "actors", "languages"}:
            setattr(movie, field, value)

    if "country" in update_data:
        country_stmt = select(CountryModel).where(
            CountryModel.code == update_data["country"]
        )
        country_result = await db.execute(country_stmt)
        country = country_result.scalar_one_or_none()
        if not country:
            country = CountryModel(
                code=update_data["country"], name=update_data["country"]
            )
            db.add(country)
            await db.flush()
        movie.country = country

    if "genres" in update_data:
        genres = []
        for genre_name in update_data["genres"]:
            genre_stmt = select(GenreModel).where(GenreModel.name == genre_name)
            genre_result = await db.execute(genre_stmt)
            genre = genre_result.scalar_one_or_none()
            if not genre:
                genre = GenreModel(name=genre_name)
                db.add(genre)
                await db.flush()
            genres.append(genre)
        movie.genres = genres

    if "actors" in update_data:
        actors = []
        for actor_name in update_data["actors"]:
            actor_stmt = select(ActorModel).where(ActorModel.name == actor_name)
            actor_result = await db.execute(actor_stmt)
            actor = actor_result.scalar_one_or_none()
            if not actor:
                actor = ActorModel(name=actor_name)
                db.add(actor)
                await db.flush()
            actors.append(actor)
        movie.actors = actors

    if "languages" in update_data:
        languages = []
        for lang_name in update_data["languages"]:
            lang_stmt = select(LanguageModel).where(LanguageModel.name == lang_name)
            lang_result = await db.execute(lang_stmt)
            language = lang_result.scalar_one_or_none()
            if not language:
                language = LanguageModel(name=lang_name)
                db.add(language)
                await db.flush()
            languages.append(language)
        movie.languages = languages

    await db.commit()
    await db.refresh(movie)

    return {"detail": "Movie updated successfully."}
