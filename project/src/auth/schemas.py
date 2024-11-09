from pydantic import BaseModel, Field
from enum import Enum as GEnum

class Gender(GEnum):
    MALE = "M"
    Female = "F"

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class User(BaseModel):
    username: str
    phone: str = Field(max_length=16, min_length=13)


class UserInDB(User):
    password: str


class UserInfoSchema(BaseModel):
    full_name: str
    age: int
    gender: Gender
    weight: float
    height: float
    user_id: int