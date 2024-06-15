from http import HTTPStatus

from fastapi import APIRouter

router = APIRouter(tags=["healthcheck"])


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    summary="Проверка работоспособности сервиса",
)
async def get_auth_history():
    return None
