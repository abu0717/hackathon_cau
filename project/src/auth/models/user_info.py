from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.models import BaseModel
from sqlalchemy import ForeignKey, Enum
from sqlalchemy import String
from src.database.types import str_64, str_256
from src.auth.manager import UserManager
from enum import Enum as GEnum


class Gender(GEnum):
    Male = "M"
    Female = "F"


class UserInfo(BaseModel):
    __tablename__ = "user_info"

    full_name: Mapped[str_64]
    age: Mapped[int]
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    weight: Mapped[float]
    height: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey('accounts.id', ondelete="CASCADE"))

    def __str__(self):
        return self.full_name
