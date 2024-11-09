from src.database.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from .products import ProductModel
from .ingredients import IngredientModel


class IngredientProductModel(BaseModel):
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    product: Mapped["ProductModel"] = relationship(back_populates="ingredients")
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    ingredient: Mapped["IngredientModel"] = relationship(back_populates='products')

    def __str__(self):
        return f"<IngredientProductModel(product_id: {self.product_id}, ingredient_id: {self.ingredient_id})>"
