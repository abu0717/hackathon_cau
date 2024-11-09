from pydantic import BaseModel
from .models import TrainingLevels, ProductTypes, AllergicIndexes, MealTimes
from src.auth.schemas import User
import datetime


class IngredientProductSchema(BaseModel):
    product_id: int
    ingredient_id: int


class IngredientSchema(BaseModel):
    name: str
    calories_per_unit: int
    allergic_index: AllergicIndexes
    allergic_percentage: int


class ProductInSchema(BaseModel):
    name: str
    description: str | None = None
    type: ProductTypes
    calories: int


class ProductSchema(ProductInSchema):
    ingredients: list[IngredientSchema]


class TrainingSchema(BaseModel):
    name: str
    video: str
    level: TrainingLevels


class MenuItemSchema(BaseModel):
    product: ProductSchema


class MenuSchema(BaseModel):
    meal_time: MealTimes
    date: datetime.date
    user: User
    items: list[ProductInSchema]
