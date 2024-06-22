from contextlib import asynccontextmanager

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from src.api.v1 import films, genres, persons
from src.core.config import config
from src.db import elastic
from src.db import cache
from src.docs.swagger_description import tags
from src.utils.check_request_limit import check_request_limit


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache.redis = Redis(host=config.redis_host, port=config.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[f"http://{config.elastic_host}:{config.elastic_port}"]
    )
    yield
    await cache.redis.close()
    await elastic.es.close()

app = FastAPI(
    version="1.0.0",
    title=config.project_name,
    summary="Async API for online cinema",
    description="Entry point for clients to search for cinema content",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    openapi_tags=tags,
    default_response_class=ORJSONResponse,
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
    contact={
        "name": "Amazing python team",
        "email": "amazaingpythonteam@fake.com",
    },
    lifespan=lifespan,
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    check_request_limit(request)
    response = await call_next(request)
    return response

app.include_router(films.router, prefix="/api/v1/films")
app.include_router(genres.router, prefix="/api/v1/genres")
app.include_router(persons.router, prefix="/api/v1/persons")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
    )
