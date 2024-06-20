import uuid as uuid
from http import HTTPStatus

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request

from src.constants.permissions import PERMISSIONS
from src.models.person import PersonWithFilms
from src.services.person import PersonService, get_person_service
from src.utils.jwt_and_roles import check_token_and_role
from src.utils.pagination import Paginator

router = APIRouter(tags=["persons"])


class PersonFilm(BaseModel):
    uuid: uuid.UUID
    roles: list[str]


class PersonFilmWithRating(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float


class Person(BaseModel):
    uuid: uuid.UUID
    full_name: str
    films: list[PersonFilm] | None


@router.get(
    "/search",
    response_model=list[Person],
    summary="Полнотекстовый поиск по персонам",
    description="Получение информации по персонам посредством полнотекстового поиска",
)
async def person_search(
    request: Request,
    query: str,
    paginated_params: Paginator = Depends(),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    await check_token_and_role(request, PERMISSIONS["can_search_persons"])

    persons_list = await person_service.search_for_a_person(
        query, paginated_params.page_number, paginated_params.page_size
    )
    return [
        Person(
            uuid=movie_person["uuid"],
            full_name=movie_person["full_name"],
            films=movie_person["films"],
        )
        for movie_person in persons_list
    ]


@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Получение персоны по ее uuid",
    description="Возвращает данные о персоне по id",
)
async def person(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> PersonWithFilms:
    movie_person = await person_service.get_by_id(person_id)
    if not movie_person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Персона с id {person_id} не найдена",
        )

    return movie_person


@router.get(
    "/{person_id}/film/",
    response_model=list[PersonFilmWithRating],
    summary="Получение фильмов персоны по ее uuid",
    description="Возвращает фильмы по id персоны",
)
async def person_films(
    request: Request,
    person_id: str,
    person_service: PersonService = Depends(get_person_service)
) -> list[PersonFilmWithRating]:
    await check_token_and_role(request, PERMISSIONS["can_get_film_by_person"])

    films = await person_service.get_only_person_films(person_id)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Фильмы персоны с id {person_id} не найдены",
        )

    return films
