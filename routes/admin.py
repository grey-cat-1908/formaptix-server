import secrets

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, delete

import database
from models import settings, user, DeleteUser
from .utils import Admin, hash_password

router = APIRouter(prefix="/admin")


@router.post("/user")
async def create_user(auth: user.Auth, admin_token: Admin):
    if len(auth.username.strip()) == 0:
        raise HTTPException(400, "Username must not be empty")
    if len(auth.password.strip()) == 0:
        raise HTTPException(400, "Password must not be empty")
    if settings.DISABLE_ADMIN:
        raise HTTPException(403, "You are not admin")

    salt = secrets.token_hex(8)

    async with database.sessions.begin() as session:
        stmt = select(database.User).where(
            database.User.username == auth.username.strip()
        )
        db_request = await session.execute(stmt)
        user = db_request.scalar_one_or_none()
        if user is not None:
            raise HTTPException(400, "User with this username already exists")

        new_user = database.User(
            username=auth.username.strip(),
            password=hash_password(auth.password.strip(), salt),
            salt=salt,
        )
        session.add(new_user)


@router.delete("/user")
async def delete_user(user: DeleteUser, admin_token: Admin):
    async with database.sessions.begin() as session:
        stmt = delete(database.User).where(
            database.User.username == user.username.strip()
        )
        await session.execute(stmt)
