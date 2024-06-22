import asyncio
from typing import Any
from urllib.parse import urljoin

import aiohttp
import jwt
import pytest
from redis.asyncio import Redis

from .settings import test_settings
from ...utils.general import calculate_iat_and_exp_tokens


@pytest.fixture(scope="session")
async def event_loop(request):
    """Event_loop для scope='session'"""

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def clean_cache():
    """Удаление всех ключей из Redis (из текущей db)"""

    redis = Redis.from_url(
        f"redis://{test_settings.REDIS.REDIS_HOST}:{test_settings.REDIS.REDIS_PORT}",
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
        url = urljoin(test_settings.MOVIES_API_URL, endpoint)
        async with client_session.get(url, params=params) as raw_response:
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
        async with client_session_w_tokens.get(url, params=params) as raw_response:
            response = await raw_response.json()
            status = raw_response.status

            return status, response

    return inner


@pytest.fixture(scope="session")
async def access_token_admin():
    """Creates access token"""

    iat, exp_access_token, _ = await calculate_iat_and_exp_tokens()

    headers = {"alg": test_settings.AUTH_ALGORITHM, "typ": "JWT"}

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
        test_settings.PRIVATE_KEY,
        algorithm=test_settings.AUTH_ALGORITHM,
        headers=headers,
    )

    return encoded_access_token


@pytest.fixture(scope="session")
async def refresh_token_admin():
    """Creates refresh token"""

    iat, _, exp_refresh_token = await calculate_iat_and_exp_tokens()

    headers = {"alg": test_settings.AUTH_ALGORITHM, "typ": "JWT"}

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
        test_settings.PRIVATE_KEY,
        algorithm=test_settings.AUTH_ALGORITHM,
        headers=headers,
    )

    return encoded_refresh_token


@pytest.fixture(scope="session")
async def access_token_unknown_role():
    """Creates access token"""

    iat, exp_access_token, _ = await calculate_iat_and_exp_tokens()

    headers = {"alg": test_settings.AUTH_ALGORITHM, "typ": "JWT"}

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
        test_settings.PRIVATE_KEY,
        algorithm=test_settings.AUTH_ALGORITHM,
        headers=headers,
    )

    return encoded_access_token
