from fastapi import APIRouter, HTTPException
from sqlalchemy import select

import database
from models import FormData, Form
from .utils import User

router = APIRouter(prefix="/form")


@router.post("/create")
async def create_form(user: User, form_data: FormData) -> Form:
    async with database.sessions.begin() as session:
        form = database.Form(
            name=form_data.name, owner_id=user.id, data=form_data.model_dump()
        )

        session.add(form)
        await session.flush()
        await session.refresh(form)

        return Form.model_validate(form)


@router.delete("/delete")
async def delete_form(user: User, id: int):
    async with database.sessions.begin() as session:
        stmt = select(database.Form).where(database.Form.id == id)
        db_request = await session.execute(stmt)
        form = db_request.scalar_one_or_none()

        if form is None:
            raise HTTPException(404, "Form not found")
        if form.owner_id != user.id:
            raise HTTPException(403, "Forbidden")

        await session.delete(form)


@router.get("/list")
async def user_forms(user: User):
    async with database.sessions.begin() as session:
        return {
            "forms": [
                Form.model_validate(item)
                for item in await session.scalars(
                    select(database.Form).where(database.Form.owner_id == user.id)
                )
            ]
        }


@router.get("/get")
async def get_form(id: int) -> Form:
    async with database.sessions.begin() as session:
        stmt = select(database.Form).where(database.Form.id == id)
        db_request = await session.execute(stmt)
        form = db_request.scalar_one_or_none()

        return Form.model_validate(form)
