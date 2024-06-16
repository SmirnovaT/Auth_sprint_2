#### AUTH SERVICE FOR ONLINE CINEMA

____________________________________________________________________________
Как запустить проект и проверить его работу
____________________________________________________________________________

Запуск приложения с docker compose

```
cd auth_service/
cp .env_example .env
```

```
docker-compose up --build
or
docker-compose up --build -d
```

Запуск приложения для локальной разработки

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
```

Создание пользователя с ролью 'admin' с помощью CLI

```
1. cd auth_service
2. python3 -m src.commands.main_cli admin strongpassword admin@mail.ru admin 
   or with first name and/or last name:
   python3 -m src.commands.main_cli admin strongpassword admin@mail.ru admin Ivan Petrov
   
If you heed help, please use: python3 -m src.commands.main_cli --help 
```

Тестирование приложения локально:

```
TBA
```

___
Работа с DB

Создать новую миграцию:
```
 alembic revision --autogenerate -m "migration name"
```
Накатить миграцию на БД:
```
alembic upgrade head
```

___
Работа с Яндекс OAuth

>Name: Online Cinema

>Redirect URI (local test): https://tolocalhost.com/api/v1/login/oauth/yandex/redirect

>Приложение в Яндекс OAuth зарегистрировано на: kristina@melikova.ru


Для локального тестирования функционала сервиса с Яндекс OAuth нужны следующие шаги:
```
1.В сервисе Яндекс OAuth прописываем Redirect URI:
https://tolocalhost.com/api/v1/login/oauth/yandex/redirect
2. В браузер вставляем адрес:
http://0.0.0.0:8000/api/v1/login/oauth/yandex/
3. Нажимаем "Войти как ..."
4. На tolocalhost.com выставляем галку для активации редиректа,
   указываем port: 8000, host: localhost
5. Оказываемся тут --> "/oauth/{oauth_provider}/redirect"
6. Далее выполнится остальная необходимая логика для логина пользователя
```