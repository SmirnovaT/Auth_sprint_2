import time
import logging
import os

import psycopg2


dsn = {
    "dbname": os.environ.get("POSTGRES_DB", "postgres"),
    "user": os.environ.get("POSTGRES_USER", "app"),
    "password": os.environ.get("POSTGRES_PASSWORD", "123qwe"),
    "host": os.environ.get("POSTGRES_HOST", "users_db"),
    "port": os.environ.get("POSTGRES_PORT", 5432),
    "options": "-c search_path=content",
}
conn_pg = psycopg2.connect(**dsn).cursor()
while True:
    time.sleep(10)
    try:
        conn_pg.execute("""SELECT 1;""")
        break
    except Exception as e:
        logging.error(f"Couldn't connect to postgres: {e}")
