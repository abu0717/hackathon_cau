from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Body, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.database.database import get_session
from .schemas import Token, User, UserInDB
from .models import AccountModel, SessionModel
from .manager import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix='/account', tags=['account'])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session)
) -> Token:
    user: AccountModel | None = (await session.execute(
        select(AccountModel).filter(AccountModel.username == form_data.username)
    )).scalars().one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.verify_password(form_data.password, user.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await user.create_access_token(
            session,
            data={"username": user.username},
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post('/')
async def create_account(response: Response, data: UserInDB = Body(), session: AsyncSession = Depends(get_session)):
    user = AccountModel(username=data.username, password=AccountModel.get_password_hash(data.password), phone=data.phone)
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
    return User(username=user.username, phone=user.phone)


@router.get("/", response_model=User)
async def get_me(
    user_session: SessionModel = Depends(AccountModel.get_current_user),
):
    if user_session.active:
        return User(username=user_session.user.username, phone=user_session.user.phone)
    raise HTTPException(status_code=400, detail="Inactive user")
