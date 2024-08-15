from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from pydantic import ValidationError

import database
from models import AnswerData, Answer

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
