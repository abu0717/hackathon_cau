from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    phone: str = Field(max_length=16, min_length=13)


class UserInDB(User):
    password: str
