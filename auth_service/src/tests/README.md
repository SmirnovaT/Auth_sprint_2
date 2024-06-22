____________________________________________________________________________
Тестирование
____________________________________________________________________________

Локальное тестирование

```
1. cd auth_service/
2. cp .env_example .env
3. python3.12 -m venv auth_venv
4. source auth_venv/bin/activate
5. pip3 install poetry
6. poetry install (or python3 -m poetry install)
7. docker run -p 6379:6379 redis:7.2.4-alpine
8. docker run -d \
  --name auth_postgres \
  -p 5432:5432 \
  -v $HOME/postgresql/data:/var/lib/postgresql/data \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres  \
  postgres:13
9. alembic upgrade head
10. uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
11. cd tests/
12. cp .env_example_test .env
```

Запустить все тесты
```
python3 -m pytest
```
Запустить все тесты в конкретном файле
```
python3 -m pytest src/<file with tests>
```

Запустить один конкретный тест
```
python3 -m pytest -k <test_name>
```
