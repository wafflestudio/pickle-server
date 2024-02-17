from typing import Optional
from ninja import Schema


class UserCreateIn(Schema):
    email: str
    username: str
    password: str


class UserLoginIn(Schema):
    email: str
    password: str


class UserSchema(Schema):
    id: int
    email: str
    username: str
    image: Optional[str]
