from src.database.models import BaseModel
from src.database.types import str_64, str_256
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ProductModel(BaseModel):
    __tablename__ = "products"

    name: Mapped[str_64] = mapped_column(unique=True)
    description: Mapped[str_256] = mapped_column(nullable=True)
    ingredients: Mapped[list["IngredientProductModel"]] = relationship(back_populates="product")

    def __str__(self):
        return f"<ProductModel(name: {self.name}, description: {self.description})>"

from .m2m import IngredientProductModel