from enum import Enum, auto

from pydantic import Field

from models import BaseModel


class QuestionType(Enum):
    text = auto()


class BaseQuestion(BaseModel):
    question_type: QuestionType
    label: str = Field(min_length=1)
    description: str | None = Field(None, min_length=1)


class TextQuestion(BaseQuestion):
    question_type = QuestionType.text
    min_length: int | None = None
    max_length: int | None = None
