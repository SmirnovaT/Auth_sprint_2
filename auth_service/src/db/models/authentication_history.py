import uuid

from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.postgres import Base
from src.utils.mixins import TimestampMixin


class AuthenticationHistory(Base, TimestampMixin):
    __tablename__ = "authentication_histories"
    __table_args__ = {"comment": "История аутентификации пользователей"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
        comment="Идентификатор аутентификации",
    )
    success = Column(
        Boolean,
        nullable=False,
        comment="Флаг, указывающий, был ли вход успешным (True) или нет (False)",
    )
    user_agent = Column(
        String, comment="Информация о браузере и операционной системе пользователя"
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="Идентификатор пользователя, связанного с этой записью о входе",
    )
    user = relationship("User", back_populates="authentication_histories")
