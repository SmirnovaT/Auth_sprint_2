from http import HTTPStatus
from urllib.parse import urljoin

import pytest

from settings import (test_settings)
from test_data.user import (
    registration_data,
    change_login_data,
    change_login_wrong_data,
    only_login_data,
    only_login_data_wrong,
    only_password_data,
    only_password_data_wrong
)


USER_ENDPOINT = "/auth/api/v1/user"
USER_URL = urljoin(test_settings.auth_api_url, USER_ENDPOINT)

pytestmark = pytest.mark.asyncio


async def test_refresh_token_401(make_post_request):
    status, response = await make_post_request(USER_URL + "/refresh")

    assert status == HTTPStatus.UNAUTHORIZED
    assert (
        response["detail"] == "Пользователь не авторизован, нет рефреш токена в cookies"
    )


async def test_refresh_token_200(refresh_token_unknown_role, client_session):
    client_session.cookie_jar.update_cookies(
        {"refresh_token": refresh_token_unknown_role}
    )
    headers = {"X-Request-Id": "test"}

    async with client_session.post(USER_URL + "/refresh", headers=headers) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.OK
        assert response["message"] == "Токен обновлен"


async def test_register_200(make_post_request, delete_row_from_table):
    status, response = await make_post_request(USER_URL + "/signup", registration_data)

    assert status == HTTPStatus.CREATED
    assert response["first_name"] == registration_data["first_name"]
    assert response["last_name"] == registration_data["last_name"]
    assert "password" not in response

    await delete_row_from_table("users", response["id"])


async def test_user_creating_w_already_existing_name(
    make_post_request, delete_row_from_table
):
    _, response = await make_post_request(USER_URL + "/signup", registration_data)

    status, response_error = await make_post_request(
        USER_URL + "/signup", registration_data
    )
    assert status == HTTPStatus.BAD_REQUEST
    assert response_error["detail"] == "Значение поля: 'email' не уникально"

    await delete_row_from_table("users", response["id"])


async def test_login_updating_success(
    access_token_admin, client_session, make_post_request, delete_row_from_table
):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    headers = {"X-Request-Id": "test"}

    await make_post_request(USER_URL + "/signup", registration_data)

    async with client_session.patch(
        USER_URL + "/change-password",
        json=change_login_data,
        headers=headers,
    ) as raw_response:
        response = await raw_response.json()
    assert raw_response.status == HTTPStatus.OK
    assert response["message"] == "Пароль и логин успешно обновлены"
    await delete_row_from_table(
        "users", change_login_data["password_change_data"]["new_login"], "login"
    )


async def test_login_updating_wrong(
    access_token_admin, client_session, make_post_request, delete_row_from_table
):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    headers = {"X-Request-Id": "test"}

    await make_post_request(USER_URL + "/signup", registration_data)

    async with client_session.patch(
        USER_URL + "/change-password",
        json=change_login_wrong_data,
        headers=headers,
    ) as raw_response:
        response = await raw_response.json()
    assert raw_response.status == HTTPStatus.UNAUTHORIZED
    assert response["detail"] == "Неверный логин или пароль"
    await delete_row_from_table("users", registration_data["login"], "login")


async def test_only_login_updating_success(
    access_token_admin, client_session, make_post_request, delete_row_from_table
):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    headers = {"X-Request-Id": "test"}

    await make_post_request(USER_URL + "/signup", registration_data)

    async with client_session.patch(
        USER_URL + "/change-password",
        json=only_login_data,
        headers=headers,
    ) as raw_response:
        response = await raw_response.json()
    assert raw_response.status == HTTPStatus.OK
    assert response["message"] == "Пароль и логин успешно обновлены"
    await delete_row_from_table(
        "users", only_login_data["password_change_data"]["new_login"], "login"
    )


async def test_only_login_updating_wrong(
    access_token_admin, client_session, make_post_request, delete_row_from_table
):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    headers = {"X-Request-Id": "test"}

    await make_post_request(USER_URL + "/signup", registration_data)
    async with client_session.patch(
        USER_URL + "/change-password",
        json=only_login_data_wrong,
        headers=headers,
    ) as raw_response:
        response = await raw_response.json()
    assert raw_response.status == HTTPStatus.UNAUTHORIZED
    assert response["detail"] == "Неверный логин или пароль"
    await delete_row_from_table("users", registration_data["login"], "login")


async def test_only_password_updating_success(
    access_token_admin, client_session, make_post_request, delete_row_from_table
):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    headers = {"X-Request-Id": "test"}

    await make_post_request(USER_URL + "/signup", registration_data)

    async with client_session.patch(
        USER_URL + "/change-password",
        json=only_password_data,
        headers=headers,
    ) as raw_response:
        response = await raw_response.json()
    assert raw_response.status == HTTPStatus.OK
    assert response["message"] == "Пароль и логин успешно обновлены"
    await delete_row_from_table(
        "users", only_login_data["password_change_data"]["new_login"], "login"
    )


async def test_only_password_updating_wrong(
    access_token_admin, client_session, make_post_request, delete_row_from_table
):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    headers = {"X-Request-Id": "test"}

    await make_post_request(USER_URL + "/signup", registration_data)
    async with client_session.patch(
        USER_URL + "/change-password",
        json=only_password_data_wrong,
        headers=headers,
    ) as raw_response:
        response = await raw_response.json()
    assert raw_response.status == HTTPStatus.UNAUTHORIZED
    assert response["detail"] == "Неверный логин или пароль"
    await delete_row_from_table("users", registration_data["login"], "login")
