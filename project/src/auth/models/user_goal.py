from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.models import BaseModel
from sqlalchemy import ForeignKey, Enum
from src.database.types import str_64
from datetime import datetime


class UserGoal(BaseModel):
    __tablename__ = "user_goal"

    user_id: Mapped[int] = mapped_column(ForeignKey('accounts.id', ondelete="CASCADE"))
    goal: Mapped[Enum] = mapped_column(Enum("loss", "gain", "maintain", name="goal_type"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
