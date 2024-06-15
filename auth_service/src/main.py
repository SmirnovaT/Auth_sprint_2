from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from redis.asyncio import Redis

from src.api.v1 import role, login, user, auth_history, healthcheck
from src.core.config import settings
from src.db import cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache.redis = Redis(
        host=settings.redis_host, port=settings.redis_port, decode_responses=True
    )
    yield
    await cache.redis.close()


app = FastAPI(
    version="1.0.0",
    title=settings.project_name,
    summary="Auth service for online cinema",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
    contact={
        "name": "Amazing python team",
        "email": "amazaingpythonteam@fake.com",
    },
    lifespan=lifespan,
)

add_pagination(app)

app.include_router(user.router, prefix="/api/v1/user")
app.include_router(role.router, prefix="/api/v1/role")
app.include_router(login.router, prefix="/api/v1/login")
app.include_router(auth_history.router, prefix="/api/v1/auth-history")
app.include_router(healthcheck.router, prefix="/api/v1/healthcheck")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
