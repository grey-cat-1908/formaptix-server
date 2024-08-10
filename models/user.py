from pydantic import Field

from models import BaseModel


class User(BaseModel):
    id: int
    username: str


class Auth(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    id: int
    username: str
    token: str


class DeleteUser(BaseModel):
    username: str


class UpdatePassword(BaseModel):
    password: str
