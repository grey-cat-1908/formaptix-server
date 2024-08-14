from enum import IntEnum, auto
from typing import TypeAlias
from uuid import UUID, uuid4

from pydantic import Field, field_validator

from models import BaseModel


class QuestionType(IntEnum):
    text = 1
    selector = 2


class BaseQuestion(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    question_type: QuestionType
    label: str = Field(min_length=1)
    description: str | None = Field(None, min_length=1)
    required: bool = True


class Option(BaseModel):
    label: str


class TextQuestion(BaseQuestion):
    question_type: QuestionType = QuestionType.text
    min_length: int | None = None
    max_length: int | None = None

    @field_validator("min_length")
    @classmethod
    def validate_min_length(cls, v, info):
        if v is not None and v < 0:
            raise ValueError("min_length must be greater than or equal to 0")
        return v

    @field_validator("max_length")
    @classmethod
    def validate_max_length(cls, v, info):
        min_length = info.data.get("min_length")
        if v is not None:
            if v <= 0:
                raise ValueError("max_length must be greater than 0")
            if min_length is not None and v < min_length:
                raise ValueError("max_length cannot be less than min_length")
        return v


class SelectorQuestion(BaseQuestion):
    question_type: QuestionType = QuestionType.selector
    min_values: int = 1
    max_values: int | None = None
    options: list[Option] = []

    @field_validator("min_values")
    @classmethod
    def validate_min_values(cls, v, info):
        options = info.data.get("options")
        if v is not None and (v < 1 or v > len(options)):
            raise ValueError("min_values must be greater than or equal to 1")
        return v

    @field_validator("max_values")
    @classmethod
    def validate_max_values(cls, v, info):
        min_values = info.data.get("min_values")
        options = info.data.get("options")
        if v is not None and (v > len(options) or min_values > v):
            raise ValueError(
                "max_values cannot be less than min_length or greater than the number of options"
            )
        return v


Question: TypeAlias = SelectorQuestion | TextQuestion


class FormData(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = Field(None, min_length=1)
    questions: list[Question] = []

    @field_validator("questions")
    @classmethod
    def validate_questions(
        cls,
        v,
        info
    ):
        questions = info.data.get("questions")
        
        uuids = set()
        for question in questions:
            uuids.add(question.question_id)

        if len(questions) != len(uuids):
            raise ValueError(
                "All questions must have different id's"
            )

        return v


class Form(BaseModel):
    id: int
    data: FormData
