import datetime
from uuid import UUID


from src.schemas.model_config import BaseOrjsonModel


class RoleGeneral(BaseOrjsonModel):
    id: UUID
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
