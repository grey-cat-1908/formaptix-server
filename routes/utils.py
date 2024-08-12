from typing import Annotated
import hashlib

import jwt
from fastapi import Depends, HTTPException, Header
from sqlalchemy import select

from models import settings
import database


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha512((password + salt).encode("utf-8")).hexdigest()


def verify_admin(password: Annotated[str, Header(alias="x-token")]):
    if password.strip() != settings.admin_password:
        raise HTTPException(401, "Unauthorized")
    return True


async def verify_user(token: Annotated[str, Header(alias="x-token")]) -> database.User:
    try:
        data = jwt.decode(
            token, algorithms=["HS256"], options={"verify_signature": False}
        )
    except jwt.exceptions.DecodeError:
        raise HTTPException(401, "Invalid token")

    if "sub" not in data and not isinstance(data["sub"], int):
        raise HTTPException(401, "Invalid token")

    async with database.sessions.begin() as session:
        stmt = select(database.User).where(database.User.id == data.get("sub"))
        db_request = await session.execute(stmt)
        user = db_request.scalar_one_or_none()

        if user is None:
            raise HTTPException(401, "Invalid token")

        try:
            jwt.decode(token, settings.secret + user.password, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            raise HTTPException(401, "Invalid token")

        session.expunge(user)
        return user


User = Annotated[database.User, Depends(verify_user, use_cache=False)]
Admin = Annotated[bool, Depends(verify_admin, use_cache=False)]
