from http import HTTPStatus
from urllib.parse import urljoin

import pytest

from settings import test_settings

GENERAL_ROLE_ENDPOINT = "auth/api/v1/role"
GENERAL_ROLE_URL = urljoin(test_settings.auth_api_url, GENERAL_ROLE_ENDPOINT)

pytestmark = pytest.mark.asyncio


async def test_get_all_roles_wo_access_401(client_session):
    client_session.cookie_jar.clear()
    headers = {"X-Request-Id": "test"}

    async with client_session.get(GENERAL_ROLE_URL, headers=headers) as raw_response:
        response = await raw_response.json()

    assert raw_response.status == HTTPStatus.UNAUTHORIZED
    assert response["detail"] == "В cookies отсутствует access token"


async def test_get_all_roles_w_wrong_role_403(
    access_token_unknown_role, client_session
):
    client_session.cookie_jar.update_cookies(
        {"access_token": access_token_unknown_role}
    )
    headers = {"X-Request-Id": "test"}

    async with client_session.get(GENERAL_ROLE_URL, headers=headers) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.FORBIDDEN
        assert response["detail"] == "Нет прав для совершения действия"


async def test_get_all_roles_success_200(access_token_admin, client_session):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    headers = {"X-Request-Id": "test"}

    async with client_session.get(GENERAL_ROLE_URL, headers=headers) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.OK
        assert len(response) == 3
        assert response[0]["name"] == "admin"
        assert response[1]["name"] == "general"
        assert response[2]["name"] == "subscriber"


async def test_role_creating_w_already_existing_name(
    access_token_admin,
    client_session,
):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    params = {"role_name": "admin"}
    headers = {"X-Request-Id": "test"}

    async with client_session.post(
            GENERAL_ROLE_URL, params=params, headers=headers,
    ) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.BAD_REQUEST
        assert response["detail"] == (
            f"Роль с названием '{params['role_name']}' " f"уже существует"
        )


async def test_role_creating_success(access_token_admin, client_session):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    params = {"role_name": "new_role"}
    headers = {"X-Request-Id": "test"}

    async with client_session.post(
            GENERAL_ROLE_URL, params=params, headers=headers,
    ) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.CREATED
        assert "id" in response
        assert response["name"] == "new_role"
        assert isinstance(response["created_at"], str)
        assert response["updated_at"] is None

    await client_session.delete(
        GENERAL_ROLE_URL, params={"role_name": params["role_name"]}
    )


async def test_role_updating_not_found(access_token_admin, client_session):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    non_existent_role_name = "old_role_name"
    params = {"new_role_name": "some_role_for_updating"}
    headers = {"X-Request-Id": "test"}

    async with client_session.patch(
        GENERAL_ROLE_URL + f"/{non_existent_role_name}",
        params=params,
        headers=headers,
    ) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.NOT_FOUND
        assert (
            response["detail"]
            == f"Роли с name '{non_existent_role_name}' не существует"
        )


async def test_role_updating_success(access_token_admin, client_session):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    old_role_name = "subscriber"
    params = {"new_role_name": "some_role_for_updating"}
    headers = {"X-Request-Id": "test"}

    async with client_session.patch(
        GENERAL_ROLE_URL + f"/{old_role_name}",
        params=params,
        headers=headers,
    ) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.OK
        assert "id" in response
        assert response["name"] == params["new_role_name"]
        assert isinstance(response["created_at"], str)
        assert isinstance(response["updated_at"], str)

    await client_session.patch(
        GENERAL_ROLE_URL + f"/{response['name']}",
        params={"new_role_name": old_role_name},
    )


async def test_role_deleting_not_found(access_token_admin, client_session):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    params = {"role_name": "role_name_to_delete"}
    headers = {"X-Request-Id": "test"}

    async with client_session.delete(
            GENERAL_ROLE_URL, params=params, headers=headers,
    ) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.NOT_FOUND
        assert (
            response["detail"] == f"Роли с name '{params['role_name']}' не существует"
        )


async def test_role_deleting_success(access_token_admin, client_session):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    params = {"role_name": "subscriber"}
    headers = {"X-Request-Id": "test"}

    async with client_session.delete(
            GENERAL_ROLE_URL, params=params, headers=headers,
    ) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.NO_CONTENT
        assert response is None

    await client_session.post(GENERAL_ROLE_URL, params={"role_name": "subscriber"})
