from sqlalchemy import Column, DateTime, func


class TimestampMixin:
    """Класс-миксин для Даты создания и Даты редактирования"""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Дата создания записи",
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Дата обновления записи",
    )
