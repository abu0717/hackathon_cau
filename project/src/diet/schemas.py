from pydantic import BaseModel
from .models import IngredientProductModel


class IngredientInSchema(BaseModel):
    name: str
    calories_per_unit: int
    allergic_index: int
    allergic_percentage: int


class IngredientSchema(IngredientInSchema):
    products: list[IngredientProductModel]


class ProductInSchema(BaseModel):
    name: str
    description: str


class ProductSchema(ProductInSchema):
    ingredients: list[IngredientSchema]
