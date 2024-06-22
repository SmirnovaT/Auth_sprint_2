import asyncio
import logging
import time
from http import HTTPStatus

import aiohttp


async def get_status(service_url, client):
    raw_response = await client.get(service_url)
    return raw_response.status


async def wait_for_ok(service_url):
    async with aiohttp.ClientSession() as client:
        for _ in range(100):
            time.sleep(10)
            try:
                status = await get_status(service_url, client)
                if status == HTTPStatus.OK:
                    break
            except Exception as e:
                logging.error(e)


service_url = "http://auth-service:8010/api/v1/healthcheck"
loop = asyncio.new_event_loop()
loop.run_until_complete(wait_for_ok(service_url))
