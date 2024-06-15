from typing import Annotated, Optional

import typer
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.logger import auth_logger
from src.db.models import User, Role

ENGINE = create_engine(f"postgresql+psycopg2://{settings.db_dsn}")


def create_admin(
    login: Annotated[str, typer.Argument()],
    password: Annotated[str, typer.Argument()],
    email: Annotated[str, typer.Argument()],
    role_name: Annotated[str, typer.Argument()],
    first_name: Annotated[Optional[str], typer.Argument()] = None,
    last_name: Annotated[Optional[str], typer.Argument()] = None,
):
    """
    CLI command for user with admin role creation
    """
    try:
        with Session(ENGINE) as session:
            admin_role = session.scalar(
                select(Role).where(Role.name == role_name)
            )
            if not admin_role:
                admin_role = Role(name=role_name)
                session.add(admin_role)
                session.commit()
                session.refresh(admin_role)

            admin_user = session.scalar(
                select(User).where(User.login == login)
            )
            if not admin_user:
                admin_user = User(
                    login=login,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                try:
                    session.add(admin_user)
                    session.commit()
                    session.refresh(admin_user)

                    admin_user.role_id = admin_role.id
                    session.commit()

                    auth_logger.info(
                        f"Создан админ '{admin_user.login}' "
                        f"с ролью '{role_name}'",
                    )

                    SystemExit(0)
                except IntegrityError as db_err:
                    auth_logger.error(
                        f"Ошибка при создании админа - одно из полей не уникально: {db_err}",
                    )

                    raise SystemExit(1)

            if admin_user.role_id != admin_role.id:
                admin_user.role_id = admin_role.id
                session.commit()

                auth_logger.info(
                    f"Админ '{admin_user.login}' существует, "
                    f"для него назначена роль '{role_name}'",
                )

            raise SystemExit(0)

    except Exception as exc:
        auth_logger.error(f"Ошибка при создании админа (суперюзера): {exc}")

        raise SystemExit(1)


if __name__ == "__main__":
    typer.run(create_admin)
