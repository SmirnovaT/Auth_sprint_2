____________________________________________________________________________
Тестирование
____________________________________________________________________________

Локальное тестирование

```
1. cp .env_example_test .env

2. docker run -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" krissmelikova/awesome_repository:v1

3. docker run -p 6379:6379 redis:7.2.4-alpine

4. (from fastapi-solutions directory) gunicorn src.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

5. cd tests/functional
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
