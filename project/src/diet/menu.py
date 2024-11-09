from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .models import ProductModel, ProductTypes
from .models import MenuModel, MenuItemModel, MealTimes
from src.auth.models import AccountModel


async def generate_menu(
        user: AccountModel,
        meal_time: MealTimes,
        date: datetime.date,
        calories: tuple[int, int],
        types_amount: dict[ProductTypes, int],
        session: AsyncSession
) -> MenuModel:
    """
    :param user: that user who needs a menu
    :param meal_time: which meal time a menu takes
    :param date: that date user going to use this menu
    :param calories: tuple of min and max calories like (min, max)
    :param types_amount: amount of meals this menu takes
    :param session: database session
    :return: menu which includes products list for any meal time
    """

    selected_products = []
    total_calories = 0

    for product_type, amount in types_amount.items():
        if amount > 0:
            query = (
                select(ProductModel.id, ProductModel.type)
                .filter(ProductModel.type == product_type)
                .order_by(func.random())
                .limit(amount)
            )
            products = (await session.execute(query)).all()
            selected_products.extend(products)
            total_calories += sum(p[1] for p in products)
    if not (calories[0] <= total_calories <= calories[1]):
        raise ValueError("not found products for given amount of type")
    menu = MenuModel(user_id=user.id, date=date, meal_time=meal_time)
    session.add(menu)
    await session.commit()
    menu_items = []
    for product in selected_products:
        menu_items.append(MenuItemModel(menu_id=menu.id, product_id=product[0]))
    session.add_all(menu_items)
    await session.commit()
    return menu