#### AUTH FOR ONLINE CINEMA SERVICE

____________________________________________________________________________
[Ссылка на репозиторий](https://github.com/SmirnovaT/Auth_sprint_2)
____________________________________________________________________________

____________________________________________________________________________
Как запустить проект и проверить его работу
____________________________________________________________________________
Необходимо заполнить .env по шаблону .env_example внутри каждого сервиса

[auth_service](auth_service/.env_example)

[fastapi_solutions](auth_service/.env_example)

[django_admin](auth_service/.env_example)


Поднимается сервис с помощью docker compose из корня проекта
```
docker-compose up --build
or
docker-compose up --build -d
```
Для локального запуска необходимо следовать инструкциям в README.md сервисов:

[auth_service](auth_service/README.md)

[fastapi_solutions](fastapi_solutions/README.md)

[django_admin](django_admin/README.md)