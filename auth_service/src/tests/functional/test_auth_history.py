from http import HTTPStatus
from urllib.parse import urljoin

import pytest

from settings import test_settings
from test_data.user import registration_data

AUTH_HISTORY_ENDPOINT = "auth/api/v1/auth-history"
AUTH_HISTORY_URL = urljoin(test_settings.auth_api_url, AUTH_HISTORY_ENDPOINT)

USER_ENDPOINT = "auth/api/v1/user"
USER_URL = urljoin(test_settings.auth_api_url, USER_ENDPOINT)

pytestmark = pytest.mark.asyncio


async def test_get_all_auth_histories_wo_access_401(
    client_session,
    delete_row_from_table,
    make_post_request,
):
    client_session.cookie_jar.clear()
    headers = {"X-Request-Id": "test"}

    _, registration_response = await make_post_request(
        USER_URL + "/signup", registration_data
    )

    async with client_session.get(
        AUTH_HISTORY_URL + f"/{registration_response["id"]}",
        headers=headers,
    ) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.UNAUTHORIZED
        assert response["detail"] == "В cookies отсутствует access token"

        await delete_row_from_table("users", registration_response["id"])


async def test_all_auth_histories_success_200(
    put_data,
    access_token_admin,
    client_session,
    delete_row_from_table,
    make_post_request,
):
    client_session.cookie_jar.update_cookies({"access_token": access_token_admin})
    headers = {"X-Request-Id": "test"}

    _, registration_response = await make_post_request(
        USER_URL + "/signup", registration_data
    )

    auth_history_new = [
        {
            "id": "1ed4dd3b-6235-4920-ab23-d51bafb5cbb2",
            "success": True,
            "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "user_id": registration_response["id"],
            "created_at": "2024-06-08 19:56:07.125360 +00:00",
        },
        {
            "id": "97ac142b-8148-477b-811b-985340bc669e",
            "success": True,
            "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "user_id": registration_response["id"],
            "created_at": "2024-06-08 20:56:07.125360 +00:00",
        },
    ]

    await put_data("authentication_histories", auth_history_new)

    async with client_session.get(
        f"{AUTH_HISTORY_URL}/{registration_response["id"]}",
        headers=headers,
    ) as raw_response:
        response = await raw_response.json()

        assert raw_response.status == HTTPStatus.OK
        assert len(response["items"]) == 2

    await delete_row_from_table(
        "authentication_histories", "1ed4dd3b-6235-4920-ab23-d51bafb5cbb2"
    )
    await delete_row_from_table(
        "authentication_histories", "97ac142b-8148-477b-811b-985340bc669e"
    )

    await delete_row_from_table("users", registration_response["id"])
