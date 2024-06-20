from http import HTTPStatus
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.constants.permissions import PERMISSIONS
from src.core.logger import a_api_logger
from src.models.film import FilmBase
from src.models.genre import Genre
from src.models.person import Person
from src.services.film import FilmService, get_film_service
from src.utils.jwt_and_roles import check_token_and_role
from src.utils.pagination import Paginator

router = APIRouter(tags=["films"])


class Film(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float | None
    description: str
    genres: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]


@router.get(
    "/{film_id}",
    response_model=Film,
    summary="Полная информация по фильму",
    description="Получение информации о фильме по его id",
)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_film_details(film_id)
    if not film:
        a_api_logger.error("Фильм не найден")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Фильм не найден")

    return Film(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


class Films(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float | None


@router.get(
    "/",
    response_model=list[Films],
    summary="Получение всех фильмов",
    description="Получение информации по всем фильмам сервиса",
)
async def films(
    genre: uuid.UUID = None,
    sort: str = "-imdb_rating",
    paginated_params: Paginator = Depends(),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmBase]:
    return await film_service.get_all_films_from_elastic(
        genre, sort, paginated_params.page_number, paginated_params.page_size
    )


@router.get(
    "/{film_id}/similar",
    response_model=list[FilmBase],
    summary="Похожие фильмы (с такими же жанрами)",
    description="Получение информации о похожих фильмах",
)
async def similar_films(
    request: Request,
    film_id: str,
    film_service: FilmService = Depends(get_film_service)
) -> list[FilmBase]:
    await check_token_and_role(request, PERMISSIONS["can_get_similar_films"])

    films = await film_service.get_similar_films(film_id)
    if not films:
        a_api_logger.error("Фильм не найден")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Фильм не найден")
    return films


@router.get(
    "/search/",
    response_model=list[Films],
    summary="Полнотекстовый поиск фильмов",
    description="Получение информации по фильмам посредством полнотекстового поиска",
)
async def search_film(
    request: Request,
    search: str,
    paginated_params: Paginator = Depends(),
    film_service: FilmService = Depends(get_film_service),
) -> list[Films] | None:
    await check_token_and_role(request, PERMISSIONS["can_search_films"])

    films = await film_service.search_film(
        search, paginated_params.page_number, paginated_params.page_size
    )
    if len(films) > 0:
        return films
    else:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Не найдено ни одного фильма",
        )
