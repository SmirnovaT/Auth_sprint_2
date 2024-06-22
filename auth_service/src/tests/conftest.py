import asyncio
import datetime
from typing import Any
from urllib.parse import urljoin

import aiohttp
import asyncpg
import jwt
import pytest
from redis.asyncio import Redis

from .settings import test_settings
from .utils.jwt import calculate_iat_and_exp_tokens


@pytest.fixture(scope="session")
async def event_loop(request):
    """Event_loop для scope='session'"""

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def clean_cache():
    """Удаление всех ключей из Redis (из текущей db)"""

    redis = Redis.from_url(
        f"redis://{test_settings.redis.redis_host}:{test_settings.redis.redis_port}",
    )
    await redis.flushdb()
    yield redis
    await redis.close()


@pytest.fixture(scope="session")
async def client_session() -> aiohttp.ClientSession:
    """AIOHTTP - сессия"""

    client_session = aiohttp.ClientSession()
    yield client_session
    await client_session.close()


@pytest.fixture(scope="session")
async def client_session_w_tokens(access_token, refresh_token) -> aiohttp.ClientSession:
    """AIOHTTP - сессия c токенами"""

    cookies = {"access_token": access_token, "refresh_token": refresh_token}
    client_session = aiohttp.ClientSession(cookies=cookies)

    yield client_session
    await client_session.close()


@pytest.fixture(scope="session")
async def make_get_request(client_session):
    """Отправка GET - запроса c AIOHTTP - сессией"""

    async def inner(endpoint: str, params: dict | None = None) -> tuple[Any, Any]:
        params = params or {}
        url = urljoin(test_settings.auth_api_url, endpoint)
        headers = {"X-Request-Id": "test"}
        async with client_session.get(url, params=params, headers=headers) as raw_response:
            response = await raw_response.json()
            status = raw_response.status

            return status, response

    return inner


@pytest.fixture(scope="session")
async def make_get_request_w_tokens(client_session_w_tokens):
    """Отправка GET - запроса c AIOHTTP - сессией"""

    async def inner(endpoint: str, params: dict | None = None) -> tuple[Any, Any]:
        params = params or {}
        url = urljoin(test_settings.auth_api_url, endpoint)
        headers = {"X-Request-Id": "test"}
        async with client_session_w_tokens.get(
                url, params=params, headers=headers,
        ) as raw_response:
            response = await raw_response.json()
            status = raw_response.status

            return status, response

    return inner


@pytest.fixture(scope="session")
async def make_post_request(client_session):
    """Отправка POST-запроса с AIOHTTP - сессией"""

    async def inner(endpoint: str, data: dict | None = None) -> tuple[Any, Any]:
        data = data or {}
        url = urljoin(test_settings.auth_api_url, endpoint)
        headers = {"X-Request-Id": "test"}
        async with client_session.post(url, json=data, headers=headers) as raw_response:
            response = await raw_response.json(content_type=None)
            status = raw_response.status
            return status, response

    return inner


@pytest.fixture(scope="session")
async def make_post_request_w_user_agent(client_session_w_user_agent):
    """Отправка POST-запроса с AIOHTTP - сессией"""

    async def inner(endpoint: str, data: dict | None = None) -> tuple[Any, Any]:
        data = data or {}
        url = urljoin(test_settings.auth_api_url, endpoint)
        headers = {"X-Request-Id": "test"}
        async with client_session_w_user_agent.post(
                url, json=data, headers=headers,
        ) as raw_response:
            response = await raw_response.json(content_type=None)
            status = raw_response.status
            return status, response

    return inner


@pytest.fixture(scope="session")
async def access_token_unknown_role():
    """Creates access token"""

    iat, exp_access_token, _ = await calculate_iat_and_exp_tokens()

    headers = {"alg": test_settings.auth_algorithm, "typ": "JWT"}

    access_token_payload = {
        "iss": "Auth service",
        "user_login": "test_login",
        "user_role": "unknown_role",
        "type": "access",
        "exp": exp_access_token,
        "iat": iat,
    }

    encoded_access_token: str = jwt.encode(
        access_token_payload,
        test_settings.private_key,
        algorithm=test_settings.auth_algorithm,
        headers=headers,
    )

    return encoded_access_token


@pytest.fixture(scope="session")
async def access_token_admin():
    """Creates access token"""

    iat, exp_access_token, _ = await calculate_iat_and_exp_tokens()

    headers = {"alg": test_settings.auth_algorithm, "typ": "JWT"}

    access_token_payload = {
        "iss": "Auth service",
        "user_login": "admin",
        "user_role": "admin",
        "type": "access",
        "exp": exp_access_token,
        "iat": iat,
    }

    encoded_access_token: str = jwt.encode(
        access_token_payload,
        test_settings.private_key,
        algorithm=test_settings.auth_algorithm,
        headers=headers,
    )

    return encoded_access_token


@pytest.fixture(scope="session")
async def refresh_token_admin():
    """Creates refresh token"""

    iat, _, exp_refresh_token = await calculate_iat_and_exp_tokens()

    headers = {"alg": test_settings.auth_algorithm, "typ": "JWT"}

    refresh_token_payload = {
        "iss": "Auth service",
        "user_login": "admin",
        "user_role": "admin",
        "type": "refresh",
        "exp": exp_refresh_token,
        "iat": iat,
    }

    encoded_refresh_token: str = jwt.encode(
        refresh_token_payload,
        test_settings.private_key,
        algorithm=test_settings.auth_algorithm,
        headers=headers,
    )

    return encoded_refresh_token


@pytest.fixture(scope="session")
async def refresh_token_unknown_role():
    """Creates refresh token"""

    iat, _, exp_refresh_token = await calculate_iat_and_exp_tokens()

    headers = {"alg": test_settings.auth_algorithm, "typ": "JWT"}

    refresh_token_payload = {
        "iss": "Auth service",
        "user_login": "test_login",
        "user_role": "unknown_role",
        "type": "refresh",
        "exp": exp_refresh_token,
        "iat": iat,
    }

    encoded_refresh_token: str = jwt.encode(
        refresh_token_payload,
        test_settings.private_key,
        algorithm=test_settings.auth_algorithm,
        headers=headers,
    )

    redis = Redis.from_url(
        f"redis://{test_settings.redis.redis_host}:{test_settings.redis.redis_port}",
    )
    await redis.set("test_login", encoded_refresh_token, ex=864000)
    return encoded_refresh_token


@pytest.fixture(scope="session")
async def add_user_to_table():
    async def inner(id, login, email, password):
        conn = await asyncpg.connect(
            dsn="postgresql://" + test_settings.postgres.db_dsn
        )
        await conn.execute(
            f"""INSERT INTO users (\"id\", \"login\", \"email\", \"password\") VALUES ('{id}', '{login}', '{email}', '{password}')"""
        )
        await conn.close()

    return inner


@pytest.fixture(scope="session")
async def delete_row_from_table():
    async def inner(table, id_, column="id"):
        conn = await asyncpg.connect(
            dsn="postgresql://" + test_settings.postgres.db_dsn
        )
        await conn.execute(f"""delete from {table} where {column} = '{id_}'""")
        await conn.close()

    return inner


@pytest.fixture(scope="session")
async def put_data():
    async def inner(table, data):
        conn = await asyncpg.connect(
            dsn="postgresql://" + test_settings.postgres.db_dsn
        )
        for row in data:
            row["created_at"] = datetime.datetime.strptime(
                row["created_at"], "%Y-%m-%d %H:%M:%S.%f %z"
            )
            columns = ", ".join(row.keys())
            placeholders = ", ".join(f"${i + 1}" for i in range(len(row)))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            await conn.execute(query, *row.values())
        await conn.close()

    return inner
