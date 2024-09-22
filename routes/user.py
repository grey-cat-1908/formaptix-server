import secrets

import jwt
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

import database
import models
from models import settings
from .utils import hash_password, User

router = APIRouter(prefix="/user")


@router.post("/login")
async def login(auth: models.Auth) -> models.Token:
    async with database.sessions.begin() as session:
        stmt = select(database.User).where(
            database.User.username == auth.username.strip()
        )
        request = await session.execute(stmt)
        user = request.scalar_one_or_none()

        if (
            user is None
            or hash_password(auth.password.strip(), user.salt) != user.password
        ):
            raise HTTPException(403, "Forbidden")

        return models.Token(
            id=user.id,
            username=user.username,
            token=jwt.encode(
                {"sub": user.id}, settings.SECRET + user.password, "HS256"
            ),
        )


@router.post("/get")
async def get(user: User) -> models.User:
    return models.User(id=user.id, username=user.username)


@router.put("/update/password")
async def update_password(user: User, new: models.UpdatePassword):
    if len(new.password.strip()) == 0:
        raise HTTPException(400, "Password must not be empty")

    async with database.sessions.begin() as session:
        session.add(user)
        user.salt = secrets.token_hex(8)
        user.password = hash_password(new.password.strip(), user.salt)
