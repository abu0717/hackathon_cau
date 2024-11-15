from src.database.models import BaseModel
from src.database.types import str_64
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum


class AllergicIndexes(Enum):
    LOW = 'l'
    MEDIUM = 'm'
    HIGH = 'h'


class IngredientModel(BaseModel):
    __tablename__ = "ingredients"

    name: Mapped[str_64] = mapped_column(unique=True)
    calories_per_unit: Mapped[int]
    allergic_index: Mapped[AllergicIndexes]
    allergic_percentage: Mapped[int]
    products: Mapped["IngredientProductModel"] = relationship(back_populates="ingredient")


    def __str__(self):
        return f"<IngredientModel(name: {self.name}, calories_per_unit: {self.calories_per_unit})>"


from .m2m import IngredientProductModel
