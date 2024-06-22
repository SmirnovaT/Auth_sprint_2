import uuid
import random
from http import HTTPStatus

import pytest
from werkzeug.security import generate_password_hash

LOGIN_ENDPOINT = "auth/api/v1/login"


@pytest.mark.asyncio
async def test_user_login_with_wrong_pass(
    add_user_to_table, make_post_request, delete_row_from_table
):
    id = uuid.uuid4()
    login = "User" + str(random.randint(1, 1000))
    email = "Email" + str(random.randint(1, 1000))
    password = generate_password_hash("Password")

    await add_user_to_table(id=id, login=login, email=email, password=password)
    status, response = await make_post_request(
        LOGIN_ENDPOINT, data={"user_login": login, "password": "WrongPassword"}
    )

    assert status == HTTPStatus.UNAUTHORIZED

    await delete_row_from_table("authentication_histories", id, "user_id")
    await delete_row_from_table("users", id)


@pytest.mark.asyncio
async def test_user_login_with_wrong_user(
    add_user_to_table,
    delete_row_from_table,
    make_post_request,
):
    id = uuid.uuid4()
    login = "User" + str(random.randint(1, 1000))
    email = "Email" + str(random.randint(1, 1000))
    password = generate_password_hash("Password")

    await add_user_to_table(id=id, login=login, email=email, password=password)

    status, response = await make_post_request(
        LOGIN_ENDPOINT,
        data={"user_login": "WrongUser", "password": "Password"},
    )

    assert status == HTTPStatus.UNAUTHORIZED

    await delete_row_from_table("users", id)
