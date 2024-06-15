Ссылка на репозиторий - [репозиторий](https://github.com/SmirnovaT/Auth_sprint_1)

### AUTH SERVICE

### AUTH SERVICE для онлайн-кинотеатра

____________________________________________________________________________
Как запустить проект и проверить его работу
____________________________________________________________________________

Подготавливаем переменные окружения

```
cd auth_service/
cp .env_example .env
```

Запуск приложения с docker compose

```
docker-compose up --build
or
docker-compose up --build -d
```

Запуск приложения для локальной разработки

```
1. cd auth_service

2. python3.12 -m venv venv

3. source venv/bin/activate

4. pip3 install poetry

5. poetry install (or python3 -m poetry install)

7. docker run -p 6379:6379 redis:7.2.4-alpine
 
8. uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

9. alembic upgrade head
```

Создание пользователя с ролью 'admin' с помощью CLI

```
1. cd auth_service

2. python3 -m src.commands.main_cli admin strongpassword admin@mail.ru admin 

   or with first name and/or last name
   
   python3 -m src.commands.main_cli admin strongpassword admin@mail.ru admin Ivan Petrov
   
If you heed help, please use: python3 -m src.commands.main_cli --help 
```

Тестирование приложения c docker-compose:
```
1. cd tests/

2. cp .env_example .env

3. docker-compose up --build
or
docker-compose up --build -d
```


Тестирование приложения локально:

```
1. Use test database! Change DB_DSN. 

2. cd auth_service

3. alembic upgrade head

4. cd tests/

5. cp .env_example .env

6. poetry install (or python3 -m poetry install)

7. pytest (python3 -m pytest) 
   or 
   pytest -k <test_name> (python3 -m pytest -k <test_name>)
```