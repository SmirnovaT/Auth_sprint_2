from urllib.parse import urljoin

import pytest

from src.tests.functional.settings import test_settings
from src.tests.functional.testdata.films.film_search_data import (
    films_search_data, films_search_data_for_pagination,
)

pytestmark = pytest.mark.asyncio

FILMS_ENDPOINT = "films"
GENERAL_FILMS_URL = urljoin(test_settings.MOVIES_API_URL, FILMS_ENDPOINT)


async def test_films_search_success(access_token_admin, client_session):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})

    query = "Star%2BWars"

    async with client_session.get(
            url=GENERAL_FILMS_URL + f"/search/?search={query}",
    ) as raw_response:
        response = await raw_response.json()

    assert raw_response.status == 200
    assert len(response) == 10
    assert response == films_search_data


async def test_films_search_not_found(access_token_admin, client_session):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})

    query = "L"

    async with client_session.get(
            url=GENERAL_FILMS_URL + f"/search/?search={query}",
    ) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == 404
        assert response == {"detail": "Не найдено ни одного фильма"}


async def test_films_search_pagination(access_token_admin, client_session):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})

    query = "Star%2BWars"
    params = {
        "page_number": 1,
        "page_size": 5,
    }

    async with client_session.get(
            url=GENERAL_FILMS_URL + f"/search/?search={query}",
            params=params,
    ) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == 200
        assert len(response) == params["page_size"]
        assert response == films_search_data_for_pagination


async def test_film_search_page_number_error(make_get_request):
    query = "Star%2BWars"
    params = {
        "page_number": -5,
        "page_size": 5,
    }

    status, response = await make_get_request(
        endpoint=GENERAL_FILMS_URL + f"/search/?search={query}",
        params=params,
    )

    assert status == 422
    assert response["detail"][0]["msg"] == "Input should be greater than or equal to 1"


async def test_film_search_page_size_error(make_get_request):
    query = "Star%2BWars"
    params = {
        "page_number": 1,
        "page_size": 200,
    }

    status, response = await make_get_request(
        endpoint=GENERAL_FILMS_URL + f"/search/?search={query}",
        params=params,
    )

    assert status == 422
    assert response["detail"][0]["msg"] == "Input should be less than or equal to 100"
