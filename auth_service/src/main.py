from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from redis.asyncio import Redis
from starlette.middleware.sessions import SessionMiddleware

from src.api.v1 import auth_history, healthcheck, login, role, user
from src.core.config import settings
from src.core.jaeger import configure_tracer
from src.db import cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache.redis = Redis(
        host=settings.redis_host, port=settings.redis_port, decode_responses=True
    )
    yield
    await cache.redis.close()


configure_tracer()

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


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )
    return response


app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.include_router(user.router, prefix="/api/v1/user")
app.include_router(role.router, prefix="/api/v1/role")
app.include_router(login.router, prefix="/api/v1/login")
app.include_router(auth_history.router, prefix="/api/v1/auth-history")
app.include_router(healthcheck.router, prefix="/api/v1/healthcheck")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
