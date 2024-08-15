from enum import Enum
from uuid import UUID
from typing import TypeAlias

from pydantic import field_validator, field_serializer

from models import BaseModel, form


class AnswerError(Enum):
    TOO_SHORT = "The text value is shorter than the minimum allowed length."
    TOO_LONG = "The text value is longer than the maximum allowed length."
    TOO_FEW_SELECTED = "The number of selected items is less than the minimum required."
    TOO_MANY_SELECTED = "The number of selected items is more than the maximum allowed."
    DUPLICATE_QUESTIONS = "Each value must correspond to a different question."
    INCORRECT_IDS = "The ids for some questions are incorrect."


class BaseValue(BaseModel):
    question_id: UUID
    question_type: form.QuestionType

    @field_serializer("question_id")
    def serialize_id(self, id: UUID):
        return str(id)


class TextValue(BaseValue):
    question_type: form.QuestionType = form.QuestionType.text
    value: str

    def validate(self, question: form.TextQuestion) -> None:
        if question.min_length and len(self.value) < question.min_length:
            raise ValueError(AnswerError.TOO_SHORT.value)
        if question.max_length and len(self.value) > question.max_length:
            raise ValueError(AnswerError.TOO_LONG.value)


class SelectorValue(BaseValue):
    question_type: form.QuestionType = form.QuestionType.selector
    values: set[int]

    def validate(self, question: form.SelectorQuestion) -> None:
        min_values = max(question.min_values, 1) if question.min_values else 1
        max_values = (
            min(question.max_values, question.options)
            if question.max_values
            else len(question.options)
        )

        if len(self.values) < min_values:
            raise ValueError(AnswerError.TOO_FEW_SELECTED.value)
        if len(self.values) > max_values:
            raise ValueError(AnswerError.TOO_MANY_SELECTED.value)


Value: TypeAlias = SelectorValue | TextValue


class AnswerData(BaseModel):
    values: list[Value]

    @property
    def question_uuids(self) -> dict[UUID, Value]:
        return {value.question_id: value for value in self.values}

    @field_validator("values")
    @classmethod
    def validate_values(cls, v, info):
        uuids = set()
        for value in v:
            uuids.add(value.question_id)

        if len(v) != len(uuids):
            raise ValueError(AnswerError.DUPLICATE_QUESTIONS.value)

        return v


class Answer(BaseModel):
    id: int
    form: form.Form
    data: AnswerData

    @field_validator("data")
    @classmethod
    def answer_validator(cls, v, info):
        uuids = v.question_uuids
        questions = info.data["form"].data.questions
        for question in questions:
            if question.required and question.id not in uuids:
                raise ValueError(AnswerError.REQUIRED_QUIESTION_NOT_ANSWERED.value)
            if question.question_type != uuids[question.id].question_type:
                raise ValueError(AnswerError.REQUIRED_QUIESTION_NOT_ANSWERED.value)
            uuids[question.id].validate(question)

            del uuids[question.id]

        if len(uuids) > 0:
            raise ValueError(AnswerError.INCORRECT_IDS.value)
        return v
