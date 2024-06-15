from datetime import datetime
from uuid import UUID


from src.schemas.model_config import BaseOrjsonModel


class AuthHistoryInDB(BaseOrjsonModel):
    id: UUID
    success: bool
    user_agent: str
    created_at: datetime

    class Config:
        orm_mode = True
