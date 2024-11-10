from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.models import BaseModel
from sqlalchemy import ForeignKey
from src.database.types import str_64
from datetime import datetime

class UserInfo(BaseModel):
    __tablename__ = "user_info"

    weight: Mapped[float]
    height: Mapped[float]
    chest_size: Mapped[float] = mapped_column(nullable=True)
    waist_size: Mapped[float] = mapped_column(nullable=True)
    hips_size: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user_id: Mapped[int] = mapped_column(ForeignKey('accounts.id', ondelete="CASCADE"))

    def __str__(self):
        return f"{self.weight}"