import datetime

from redis.asyncio import Redis
from http import HTTPStatus
from fastapi import HTTPException

from src.core.config import config


async def check_request_limit(request):

    redis_conn = Redis(host=config.redis_host, port=config.redis_port, db=0)
    user_agent = request.headers["user-agent"]
    user_id = user_agent
    pipe = redis_conn.pipeline()
    now = datetime.datetime.now()
    key = f'{user_id}:{now.minute}'
    pipe.incr(key, 1)
    pipe.expire(key, 59)
    result = await pipe.execute()
    request_number = result[0]
    if request_number > config.request_limit_per_minute:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Слишком много запросов от данного пользователя")
