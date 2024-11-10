from typing import Annotated
from fastapi import APIRouter, Depends, Body, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.database.database import get_session
from .schemas import Token, User, UserInDB, UserInfoSchema, UserResponse, UserGoalSchema
from .models import AccountModel, SessionModel, UserInfo, UserGoal
from .manager import credentials_exception, oauth2_scheme, UserManager
from datetime import datetime, timedelta, date
from sqlalchemy import select, desc
from fastapi import HTTPException, status
from src.diet.menu import generate_menu
from src.diet.models import MealTimes
from src.diet.models import ProductTypes

router = APIRouter(prefix='/account', tags=['account'])


@router.post("/token", response_model=Token)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_session)
) -> Token:
    user: AccountModel | None = (await session.execute(
        select(AccountModel).filter(AccountModel.username == form_data.username)
    )).scalars().one_or_none()
    if not user:
        raise credentials_exception
    if user.verify_password(form_data.password, user.password):
        access_token, user_session_id = await user.create_access_token(
            session,
            data={"username": user.username},
        )
        refresh_token = user.create_refresh_token(data={"username": user.username}, user_session_id=user_session_id)
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    raise credentials_exception


@router.post("/refresh", response_model=Token)
async def refresh(
        token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[AsyncSession, Depends(get_session)]
):
    access_token, = await UserManager.refresh_access_token(token, session)
    return Token(access_token=access_token, token_type="bearer", refresh_token=token)


@router.post('/')
async def create_account(response: Response, data: UserInDB = Body(), session: AsyncSession = Depends(get_session)):
    user = AccountModel(username=data.username, password=AccountModel.get_password_hash(data.password),
                        phone=data.phone, birth_date=data.birth_date, gender=data.gender)
    try:
        session.add(user)
        await session.commit()
    except IntegrityError as err:
        field = str(err.orig).split('.')[-1]
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "detail": [
                {
                    "type": "conflict",
                    "loc": [
                        "body",
                        field
                    ],
                    "msg": f"{field} already exists",
                    "input": data
                }
            ]
        }
    return User(username=user.username, phone=user.phone, birth_date=user.birth_date, gender=user.gender)


@router.get("/", response_model=User)
async def get_me(
        user_session: SessionModel = Depends(AccountModel.get_current_user),
):
    if user_session.active:
        return User(username=user_session.user.username, phone=user_session.user.phone, birth_date=user_session.user.birth_date, gender=user_session.user.gender)
    raise HTTPException(status_code=400, detail="Inactive user")


@router.get('/info')
async def get_user_info(
        user_session: SessionModel = Depends(AccountModel.get_current_user),
        session: AsyncSession = Depends(get_session)
):
    if user_session.active:
        stmt = select(AccountModel, UserInfo).join(UserInfo, UserInfo.user_id == AccountModel.id).filter(
            AccountModel.id == user_session.user_id)
        result = await session.execute(stmt)

        account_info, user_info = result.first()

        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User info not found")

        return {
            "username": account_info.username,
            "phone": account_info.phone,
            "weight": user_info.weight,
            "height": user_info.height,
            "chest_size": user_info.chest_size,
            "waist_size": user_info.waist_size,
            "hips_size": user_info.hips_size,
        }

    raise HTTPException(status_code=400, detail="Inactive user")


# @router.post('/user_info')
# async def user_info(user: UserInfoSchema, session: AsyncSession = Depends(get_session),
#                     user_session: SessionModel = Depends(AccountModel.get_current_user)):
#     new_user_info = UserInfo(
#         weight=user.weight,
#         height=user.height,
#         chest_size=user.chest_size,
#         waist_size=user.waist_size,
#         hips_size=user.hips_size,
#         user_id=user_session.user_id
#     )
#     session.add(new_user_info)
#     await session.commit()
#     await session.refresh(new_user_info)
#
#     return {"message": "User Info updated successfully", "user_info": new_user_info}


@router.get("/user_info")
async def get_user_info(session: AsyncSession = Depends(get_session)):
    try:
        stmt = select(UserInfo)
        result = await session.execute(stmt)
        user_info = result.scalars().all()
        if not user_info:
            return {"message": "No user info found"}
        return [
            {
                "weight": u.weight,
                "height": u.height,
                "chest_size": u.chest_size,
                "waist_size": u.waist_size,
                "hips_size": u.hips_size,
                "created_at": u.created_at
            }
            for u in user_info
        ]
    except Exception as e:
        return {"error": str(e)}


@router.post('/register')
async def register(users: UserInfoSchema, response: Response, session: AsyncSession = Depends(get_session),
                   data: UserInDB = Body()):
    user = AccountModel(username=data.username, password=AccountModel.get_password_hash(data.password),
                        phone=data.phone, birth_date=data.birth_date, gender=data.gender)

    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except IntegrityError as err:
        field = str(err.orig).split('.')[-1]
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "detail": [
                {
                    "type": "conflict",
                    "loc": [
                        "body",
                        field
                    ],
                    "msg": f"{field} already exists",
                    "input": data
                }
            ]
        }

    new_user_info = UserInfo(
        weight=users.weight,
        height=users.height,
        chest_size=users.chest_size,
        waist_size=users.waist_size,
        hips_size=users.hips_size,
        user_id=user.id
    )

    session.add(new_user_info)
    await session.commit()

    await session.refresh(new_user_info)
    age = datetime.utcnow().year - user.birth_date.year
    for_men = lambda h, w: ((10 * w) + (6.25 * h) - (5 * age) + 5, (10 * w) + (6.25 * h) - (5 * age) + 20)
    for_women = lambda h, w: ((10 * w) + (6.25 * h) - (5 * age) + 161, (10 * w) + (6.25 * h) - (5 * age) + 200)
    calories = for_men(users.weight, users.height) if user.gender else for_women

    types_amount = {
        ProductTypes.FOOD: 1,
        ProductTypes.FRUIT: 2,
        ProductTypes.DAIRY: 1
    }
    try:
        await generate_menu(
            user,
            meal_time=MealTimes.BREAKFAST,
            date=date.today(),
            calories=calories,
            types_amount=types_amount,
            session=session,
        )
    except ValueError:
        pass

    return {"message": "User Info updated successfully", "user_info": new_user_info}


@router.post('/info', response_model=UserInfoSchema)
async def post_user_info(
        new_data: UserInfoSchema,
        user_session: SessionModel = Depends(AccountModel.get_current_user),
        session: AsyncSession = Depends(get_session)
):
    if not user_session.active:
        raise HTTPException(status_code=400, detail="Inactive user")

    account = user_session.user
    one_week_ago = datetime.utcnow() - timedelta(weeks=1)
    stmt_latest = select(UserInfo).where(UserInfo.user_id == account.id).order_by(desc(UserInfo.created_at))
    result = await session.execute(stmt_latest)
    latest_info = result.scalars().first()

    if latest_info and latest_info.created_at > one_week_ago:
        raise HTTPException(status_code=403, detail="You can only input data once a week.")
    new_user_info = UserInfo(
        weight=new_data.weight,
        height=new_data.height,
        chest_size=new_data.chest_size,
        waist_size=new_data.waist_size,
        hips_size=new_data.hips_size,
        created_at=datetime.utcnow(),
        user_id=account.id
    )

    session.add(new_user_info)
    await session.commit()
    await session.refresh(new_user_info)

    return {
        "weight": new_user_info.weight,
        "height": new_user_info.height,
        "chest_size": new_user_info.chest_size,
        "waist_size": new_user_info.waist_size,
        "hips_size": new_user_info.hips_size,
    }


@router.get('/info/progress', response_model=UserResponse)
async def get_user_progress(
        user_session: SessionModel = Depends(AccountModel.get_current_user),
        session: AsyncSession = Depends(get_session)
):
    if user_session.active:
        account = user_session.user

        stmt_latest = select(UserInfo).where(UserInfo.user_id == account.id).order_by(desc(UserInfo.created_at))
        result = await session.execute(stmt_latest)
        latest_info = result.scalars().first()

        one_week_ago = datetime.utcnow() - timedelta(minutes=1)
        stmt_week_old = select(UserInfo).where(
            UserInfo.user_id == account.id,
            UserInfo.created_at <= one_week_ago
        ).order_by(desc(UserInfo.created_at))
        result = await session.execute(stmt_week_old)
        week_old_info = result.scalars().first()

        if latest_info and week_old_info:
            progress_message = "Keep up the good work!"
            if latest_info.weight < week_old_info.weight:
                progress_message = "Great job on the weight loss!"
            elif latest_info.weight > week_old_info.weight:
                progress_message = "Consider reviewing your goals."

            latest_info_dict = {key: value for key, value in latest_info.__dict__.items() if not key.startswith("_")}

            return {
                "latest_info": latest_info_dict,
                "progress_message": progress_message
            }

        raise HTTPException(status_code=404, detail="Not enough data")

    raise HTTPException(status_code=400, detail="Inactive user")


@router.post('/goal')
async def set_goal(
        goal_data: UserGoalSchema,
        user_session: SessionModel = Depends(AccountModel.get_current_user),
        session: AsyncSession = Depends(get_session)
):
    if not user_session.active:
        raise HTTPException(status_code=404, detail="Inactive user")

    account = user_session.user

    stmt = select(UserGoal).where(UserGoal.user_id == account.id)
    result = await session.execute(stmt)
    user_goal = result.scalars().first()

    if user_goal:
        user_goal.goal = goal_data.goal
        user_goal.created_at = datetime.utcnow()
    else:
        user_goal = UserGoal(
            goal=goal_data.goal,
            created_at=datetime.utcnow(),
            user_id=account.id
        )
        session.add(user_goal)
    await session.commit()
    await session.refresh(user_goal)
    return user_goal


@router.get('/goal', response_model=UserGoalSchema)
async def get_goal(
        user_session: SessionModel = Depends(AccountModel.get_current_user),
        session: AsyncSession = Depends(get_session)
):
    if not user_session.active:
        raise HTTPException(status_code=404, detail="Inactive User")

    account = user_session.user
    account = user_session.user
    stmt = select(UserGoal).where(UserGoal.user_id == account.id)
    result = await session.execute(stmt)
    user_goal = result.scalars().first()

    if not user_goal:
        raise HTTPException(status_code=404, detail="Goal not set")

    return user_goal
