from fastapi import APIRouter
from sqlalchemy import select

import database
from models import FormData, Form
from .utils import User

router = APIRouter(prefix="/form")


@router.post("/create")
async def create_form(user: User, form_data: FormData):
    async with database.sessions.begin() as session:
        form = database.Form(
            name=form_data.name, owner_id=user.id, data=form_data.model_dump()
        )

        session.add(form)
        await session.flush()
        await session.refresh(form)

        return {"status": "success", "form_id": form.id}


@router.get("/my")
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
