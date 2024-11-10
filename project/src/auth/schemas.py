import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class User(BaseModel):
    username: str
    phone: Optional[str] = Field(default=None, max_length=16, min_length=13)
    birth_date: datetime.date


class UserInDB(User):
    password: str


class UserInfoSchema(BaseModel):
    weight: float
    height: float
    chest_size: Optional[float] = None
    waist_size: Optional[float] = None
    hips_size: Optional[float] = None


class UserResponse(BaseModel):
    latest_info: dict
    progress_message: str


class GoalType(str, Enum):
    loss = "loss"
    gain = "gain"
    maintain = "maintain"


class UserGoalSchema(BaseModel):
    goal: GoalType
