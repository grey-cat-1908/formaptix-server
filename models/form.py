from enum import Enum, auto
from typing import TypeAlias

from pydantic import Field, field_validator

from models import BaseModel


class QuestionType(Enum):
    text = auto()
    choice = auto()


class BaseQuestion(BaseModel):
    question_type: QuestionType
    label: str = Field(min_length=1)
    description: str | None = Field(None, min_length=1)
    required: bool = True


class Option(BaseModel):
    label: str


class TextQuestion(BaseQuestion):
    question_type = QuestionType.text
    min_length: int | None = None
    max_length: int | None = None

    @field_validator('min_length')
    @classmethod
    def validate_min_length(cls, v, values):
        if v is not None and v < 0:
            raise ValueError('min_length must be greater than or equal to 0')
        return v

    @field_validator('max_length')
    @classmethod
    def validate_max_length(cls, v, values):
        min_length = values.get('min_length')
        if v is not None:
            if v <= 0:
                raise ValueError('max_length must be greater than 0')
            if min_length is not None and v < min_length:
                raise ValueError('max_length cannot be less than min_length')
        return v


class SelectorQuestion(BaseQuestion):
    question_type = QuestionType.choice
    min_values: int = 1
    max_values: int | None = None
    options: list[Option] = []

    @field_validator('min_values')
    @classmethod
    def validate_min_values(cls, v, values):
        options = values.get('options')
        if v is not None and (v < 1 or v > len(options)):
            raise ValueError('min_values must be greater than or equal to 1')
        return v

    @field_validator('max_values')
    @classmethod
    def validate_max_values(cls, v, values):
        min_values = values.get('min_values')
        options = values.get('options')
        if v is not None and (v > len(options) or min_values > v):
            raise ValueError('max_values cannot be less than min_length or greater than the number of options')
        return v


Question: TypeAlias = SelectorQuestion | TextQuestion


class Form(BaseModel):
    id: int
    name: str
    questions: list[Question] = []
