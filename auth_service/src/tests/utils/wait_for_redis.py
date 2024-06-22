import backoff
from redis import Redis
from redis.exceptions import ConnectionError


@backoff.on_exception(
    backoff.expo, (ConnectionError, ConnectionRefusedError), max_tries=20
)
def ping_redis(redis_client):
    redis_client.ping()


if __name__ == "__main__":
    redis_client = Redis(host="cache", port=6379)
    ping_redis(redis_client)
