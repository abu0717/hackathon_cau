from datetime import datetime
from src.auth.models import AccountModel
from src.database.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from enum import Enum

meal_dict = {
    'bt': "Breakfast",
    'sk': "Mid-Morning Snack",
    'lu': "Lunch",
    'll': "Light Lunch",
    'an': "Afternoon",
    'dr': "Dinner"
}

class MealTimes(Enum):
    BREAKFAST = 'bt'
    SNACK = 'sk'
    LUNCH = 'lu'
    L_LUNCH = 'll'
    AFTERNOON = 'an'
    DINNER = 'dr'

    def __str__(self):
        return meal_dict[self.value]


class MenuModel(BaseModel):
    __tablename__ = 'menus'

    meal_time: Mapped[MealTimes]
    date: Mapped[datetime.date]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped[AccountModel] = relationship(backref="menus")
    items: Mapped[list["MenuItemModel"]] = relationship(back_populates="menu")

    def __str__(self):
        return f"<MenuModel(meal_time: {self.meal_time}, date: {self.date})>"


class MenuItemModel(BaseModel):
    __tablename__ = 'menu_items'

    menu_id: Mapped[int] = mapped_column(ForeignKey('menus.id', ondelete='CASCADE'))
    menu: Mapped[MenuModel] = relationship(back_populates="items")
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'))

    def __str__(self):
        return f"<MenuItemModel(menu_id: {self.menu_id}, product_id: {self.product_id})>"
