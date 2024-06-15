import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from src.db.postgres import Base
from src.utils.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = {"comment": "Пользователи"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
        comment="Идентификатор пользователя",
    )
    login = Column(
        String(255), unique=True, nullable=False, comment="Логин пользователя"
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="Электронный адрес пользователя",
    )
    password = Column(String(255), nullable=False, comment="Пароль пользователя")
    first_name = Column(String(50), comment="Имя пользователя")
    last_name = Column(String(50), comment="Фамилия пользователя")

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        comment="Идентификатор роли пользователя",
    )
    role = relationship("Role", back_populates="users")

    authentication_histories = relationship(
        "AuthenticationHistory", back_populates="user"
    )

    def __init__(
        self, login: str, email: str, password: str, first_name: str, last_name: str
    ) -> None:
        self.login = login
        self.email = email
        self.password = self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.login}>"
