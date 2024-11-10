from fastapi import APIRouter, Depends, Path, HTTPException, status, Response, File, UploadFile, Form
from sqlalchemy.exc import IntegrityError
from .schemas import ProductSchema, IngredientSchema, ProductOutSchema, MenuSchema, MenuItemSchema
from .models import ProductModel, IngredientModel, IngredientProductModel, ProductTypes, MenuModel, MenuItemModel
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete
from src.database.database import get_session, AsyncSession
from src.auth.manager import UserManager
from src.auth.models import SessionModel
import aiofiles
from settings import settings

router = APIRouter(prefix='/diet', tags=['diet'])

def err_response(err):
    field = str(err.orig).split('.')[-1]
    if not field:
        field = str(err.orig).split('\n')[0].split()[-1].strip('"')
    raise HTTPException(status.HTTP_409_CONFLICT, {
            "detail": [
                {
                    "type": "conflict",
                    "loc": [
                        "body",
                        field
                    ],
                    "msg": f"{field} already exists",
                }
            ]
        }
    )


@router.get('/products', response_model=list[ProductOutSchema])
async def get_products(session: AsyncSession = Depends(get_session), _: bool = Depends(UserManager.verify_user)):
    products = ((await session.execute(
        select(ProductModel)
        .options(selectinload(ProductModel.ingredients).selectinload(IngredientProductModel.ingredient))))
         .scalars().all()
         )

    return [ProductOutSchema(
        name=p.name, description=p.description, price=p.price,
        calories=p.calories, type=p.type.value, image=p.image,
        ingredients=map(
            lambda x: IngredientSchema(
                name=x.ingredient.name,
                calories_per_unit=x.ingredient.calories_per_unit,
                allergic_index=x.ingredient.allergic_index,
                allergic_percentage=x.ingredient.allergic_percentage
            ), p.ingredients
        )) for p in products]


@router.post('/products', response_model=ProductOutSchema)
async def add_product(
        name: str = Form(...),
        description: str | None = Form(nullable=True),
        type: ProductTypes = Form(...),
        calories: int = Form(...),
        price: int = Form(),
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(UserManager.verify_user)
):
    image_path = f"media/images/{image.filename.replace(' ', '_')}"
    file_location = settings.base_dir / image_path
    product_obj = ProductModel(
        name=name,
        description=description,
        type=type,
        price=price,
        calories=calories,
        image=f"{settings.protocol}://{settings.host}/{image_path}",
    )
    session.add(product_obj)
    try:
        await session.commit()
    except IntegrityError as err:
        err_response(err)
    async with aiofiles.open(file_location, 'wb') as file:
        while content := await image.read(1024):
            await file.write(content)

    return ProductOutSchema(
        name=name,
        description=description,
        type=type,
        price=price,
        calories=calories,
        image=product_obj.image,
        ingredients=[]
    )


@router.get('/products/{id}', response_model=ProductSchema)
async def get_product(
        product_id: int = Path(alias='id'),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(UserManager.verify_user)
):
    p = ((await session.execute(
        select(ProductModel)
        .where(ProductModel.id == product_id)
        .options(selectinload(ProductModel.ingredients).selectinload(IngredientProductModel.ingredient))))
               .scalars().one_or_none()
               )
    if not p:
        raise HTTPException(status_code=404, detail='Product not found')
    return ProductSchema(
        name=p.name,
        description=p.description,
        calories=p.calories,
        price=p.price,
        type=p.type,
        ingredients=map(lambda x: IngredientSchema(
            name=x.ingredient.name,
            calories_per_unit=x.ingredient.calories_per_unit,
            allergic_index=x.ingredient.allergic_index,
            allergic_percentage=x.ingredient.allergic_percentage),
            p.ingredients
        )
    )


@router.post('/products/{id}', response_model=ProductSchema)
async def add_ingredient2product(
        *,
        product_id: int = Path(alias='id'),
        ingredients: list[IngredientSchema],
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(UserManager.verify_user)
):
    try:
        p = await session.get(ProductModel, product_id)
        if not p:
            raise HTTPException(status_code=404, detail='Product not found')
        result = list(map(lambda x: IngredientModel(**x.model_dump()), ingredients))
        session.add_all(result)
        await session.commit()
        session.add_all(map(lambda x: IngredientProductModel(product_id=product_id, ingredient_id=x.id), result))
        await session.commit()
        product = await session.get(ProductModel, product_id)
        return ProductSchema(
            name=product.name,
            description=product.description,
            type=product.type,
            price=product.price,
            calories=product.calories,
            ingredients=ingredients)
    except IntegrityError as err:
        err_response(err)


@router.delete('/products/{id}')
async def delete_product(
        *,
        response: Response,
        product_id: int = Path(alias='id'),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(UserManager.verify_user)
):
    try:
        await session.execute(delete(ProductModel).where(ProductModel.id == product_id))
        await session.commit()
    except Exception as err:
        print(type(err), err)
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    response.status_code = status.HTTP_204_NO_CONTENT


@router.post('/ingredient')
async def add_ingredient(
        *,
        data: IngredientSchema,
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(UserManager.verify_user)
):
    try:
        ingredient = IngredientModel(**data.model_dump())
        session.add(ingredient)
        await session.commit()
    except IntegrityError as err:
        err_response(err)


@router.delete('/ingredient/{id}')
async def delete_ingredient(
        *,
        response: Response,
        ingredient_id: int = Path(alias='id'),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(UserManager.verify_user)
):
    try:
        await session.execute(delete(IngredientModel).where(IngredientModel.id == ingredient_id))
        await session.commit()
    except Exception as err:
        print(type(err), err)
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    response.status_code = status.HTTP_204_NO_CONTENT


@router.put('/products/{id}', response_model=list[ProductSchema])
async def update_product(
        *,
        product_id: int = Path(alias='id'),
        ingredients: list[str],
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(UserManager.verify_user)
):
    try:
        p = await session.get(ProductModel, product_id)
        if not p:
            raise HTTPException(status_code=404, detail='Product not found')
        result = (await session.execute(select(IngredientModel.id).where(IngredientModel.name.in_(ingredients)))).scalars().all()
        session.add_all(map(lambda x: IngredientProductModel(product_id=product_id, ingredient_id=x), result))
        await session.commit()
        product = ((await session.execute(
            select(ProductModel)
            .where(ProductModel.id == product_id)
            .options(selectinload(ProductModel.ingredients).selectinload(IngredientProductModel.ingredient))))
             .scalars().one_or_none()
             )
        return ProductSchema(
            name=product.name,
            description=product.description,
            type=product.type,
            price=product.price,
            calories=product.calories,
            ingredients=map(lambda x: IngredientSchema(
                name=x.ingredient.name,
                calories_per_unit=x.ingredient.calories_per_unit,
                allergic_index=x.ingredient.allergic_index,
                allergic_percentage=x.ingredient.allergic_percentage),
                product.ingredients
            )
        )
    except IntegrityError as err:
        err_response(err)


@router.get('/ingredients', response_model=list[IngredientSchema])
async def get_ingredients(session: AsyncSession = Depends(get_session), _: bool = Depends(UserManager.verify_user)):
    ingredients = (await session.execute(select(IngredientModel))).scalars().all()
    return [
        IngredientSchema(
            name=i.name,
            calories_per_unit=i.calories_per_unit,
            allergic_index=i.allergic_index,
            allergic_percentage=i.allergic_percentage
        )
        for i in ingredients
    ]


@router.get('/menu', response_model=list[MenuSchema])
async def get_menu(
        session: AsyncSession = Depends(get_session),
        user_session: SessionModel = Depends(UserManager.get_current_user)
):
    menus = (await session.execute(
        select(MenuModel)
        .where(MenuModel.user_id == user_session.user.id)
        .options(selectinload(MenuModel.items).selectinload(MenuItemModel.product)))).scalars().all()
    return [MenuSchema(
        meal_time=menu.meal_time,
        date=menu.date,
        items=[MenuItemSchema(product=m.product) for m in menu.items]
    ) for menu in menus]
