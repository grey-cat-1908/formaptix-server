from fastapi import APIRouter, HTTPException
from sqlalchemy import select, and_
from pydantic import ValidationError

import database
from models import AnswerData, Answer
from .utils import User

router = APIRouter(prefix="/answer")


@router.post("/create")
async def create_answer(form_id: int, answer_data: AnswerData):
    async with database.sessions.begin() as session:
        answer = database.Answer(
            form_id=form_id,
            data=answer_data.model_dump(),
        )

        session.add(answer)
        await session.flush()
        await session.refresh(answer)

        try:
            answer_model = Answer.model_validate(answer)
        except ValidationError as e:
            raise HTTPException(400, e.errors()[0].get("msg"))

        return answer_model


@router.get("/get")
async def get_answers(user: User, form_id: int):
    async with database.sessions.begin() as session:
        return {
            "answers": [
                Answer.model_validate(item)
                for item in await session.scalars(
                    select(database.Answer)
                    .where(
                        and_(
                            database.Answer.form_id == form_id,
                            database.Form.owner_id == user.id,
                        )
                    )
                    .join(database.Answer.form)
                )
            ]
        }


@router.delete("/delete")
async def delete_answer(user: User, id: int):
    async with database.sessions.begin() as session:
        stmt = (
            select(database.Answer)
            .where(database.Answer.id == id)
            .join(database.Answer.form)
        )
        db_request = await session.execute(stmt)
        answer = db_request.scalar_one_or_none()

        if answer is None:
            raise HTTPException(404, "Answer not found")
        if answer.form.owner_id != user.id:
            raise HTTPException(403, "Forbidden")

        await session.delete(answer)
