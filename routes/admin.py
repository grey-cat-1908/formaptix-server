import secrets
from typing import Annotated
import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

import database
from models import settings, user

router = APIRouter(prefix="/admin")


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha512((password + salt).encode('utf-8')).hexdigest()


def verify_admin(token: str):
    if token != settings.admin_password:
        raise HTTPException(401, "Unauthorized")
    return True


Admin = Annotated[bool, Depends(verify_admin, use_cache=False)]


@router.post("/user")
async def create_user(auth: user.Auth, admin_token: Admin):
    if len(auth.username.strip()) == 0:
        raise HTTPException(400, "Username must not be empty")
    if len(auth.password.strip()) == 0:
        raise HTTPException(400, "Password must not be empty")
    if settings.disable_admin:
        raise HTTPException(403, "You are not admin")

    salt = secrets.token_hex(8)

    async with database.sessions.begin() as session:
        stmt = select(database.User).where(database.User.username == auth.username)
        db_user = session.execute(stmt).scalar_one_or_none()
        if db_user is not None:
            raise HTTPException(400, "User with this username already exists")

        new_user = database.User(
            username=auth.username,
            password=hash_password(auth.password, salt),
            salt=salt,
        )
        session.add(new_user)
        await session.flush()

        return {'status': 'Success'}