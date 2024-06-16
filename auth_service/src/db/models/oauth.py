import uuid

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.postgres import Base


class OAuthAccount(Base):
    __tablename__ = "oauth_account"
    __table_args__ = (
        UniqueConstraint("oauth_user_id", "oauth_provider_name", name="oauth_acc"),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="Идентификатор OAuth aккаунта пользователя",
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Идентификатор пользователя, связанного с OAuth аккаунтом",
    )

    oauth_user_id = Column(
        String(255),
        nullable=False,
        comment="Идентификатор пользователя у провайдера OAuth"
    )
    oauth_provider_name = Column(
        String(255),
        nullable=False,
        comment="Название провайдера OAuth"
    )

    user = relationship("User", back_populates="oauth_accounts", lazy=True)
