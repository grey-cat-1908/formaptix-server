from enum import IntEnum, Enum
from typing import Annotated, Union, Literal
from uuid import UUID, uuid4

from pydantic import Field, field_validator, field_serializer

from models import BaseModel


class FormError(Enum):
    MIN_LENGTH_ERR = "min_length must be greater than or equal to 0."
    MAX_LENGTH_ERR = "max_length must be greater than 0."
    MAX_LENGTH_LESS_THAN_MIN_LENGTH = "max_length cannot be less than min_length."
    MIN_VALUES_ERR = "min_values must be greater than or equal to 1."
    MAX_VALUES_ERR = "max_values cannot be less than min_length or greater than the number of options."
    SIMMILAR_ID_ERR = "All questions must have different id's"
    SCALE_MIN_VALUE_ERR = "min_value must be in range from 0 to 1"
    SCALE_MAX_VALUE_ERR = "max_value must be in range from 2 to 10"
    EMPTY_OPTIONS_ERR = "Options field cannot be empty"


class QuestionType(IntEnum):
    text = 1
    selector = 2
    scale = 3


class TextValidator(IntEnum):
    tin = 1
    snils = 2


class BaseQuestion(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    question_type: QuestionType
    label: str = Field(min_length=1)
    description: str | None = Field(None, min_length=1)
    image_url: str | None = None
    required: bool = True

    @field_serializer("id")
    def serialize_id(self, id: UUID):
        return str(id)


class Option(BaseModel):
    label: str
    image_url: str | None = None


class TextQuestion(BaseQuestion):
    question_type: Literal[QuestionType.text] = QuestionType.text
    validator: TextValidator | None = None
    min_length: int | None = None
    max_length: int | None = None

    @field_validator("min_length")
    @classmethod
    def validate_min_length(cls, v, info):
        validator = info.data.get("validator")
        if v is not None:
            if v < 0:
                raise ValueError(FormError.MIN_LENGTH_ERR.value)
            if validator is not None:
                return None
        return v

    @field_validator("max_length")
    @classmethod
    def validate_max_length(cls, v, info):
        min_length = info.data.get("min_length")
        validator = info.data.get("validator")
        if v is not None:
            if v <= 0:
                raise ValueError(FormError.MAX_LENGTH_TOO_SMALL.value)
            if min_length is not None and v < min_length:
                raise ValueError(FormError.MAX_LENGTH_LESS_THAN_MIN_LENGTH.value)
            if validator is not None:
                return None
        return v


class ScaleQuestion(BaseQuestion):
    question_type: Literal[QuestionType.scale] = QuestionType.scale
    min_value: int
    min_label: str | None = None
    max_value: int
    max_label: str | None = None

    @field_validator("min_value")
    @classmethod
    def validate_min_value(cls, v, info):
        if v not in [0, 1]:
            raise ValueError(FormError.SCALE_MIN_VALUE_ERR.value)
        return v

    @field_validator("max_value")
    @classmethod
    def validate_max_value(cls, v, info):
        if v < 2 or v > 10:
            raise ValueError(FormError.SCALE_MAX_VALUE_ERR.value)
        return v


class SelectorQuestion(BaseQuestion):
    question_type: Literal[QuestionType.selector] = QuestionType.selector
    min_values: int = 1
    max_values: int | None = None
    options: list[Option]

    @field_validator("options")
    @classmethod
    def validate_options(cls, v, info):
        if len(v) < 1:
            raise ValueError(FormError.EMPTY_OPTIONS_ERR.value)
        return v

    @field_validator("min_values")
    @classmethod
    def validate_min_values(cls, v, info):
        if v is not None and v < 1:
            raise ValueError(FormError.MIN_VALUES_ERR.value)
        return v

    @field_validator("max_values")
    @classmethod
    def validate_max_values(cls, v, info):
        min_values = info.data.get("min_values")
        if v is not None and min_values > v:
            raise ValueError(FormError.MAX_VALUES_ERR.value)
        return v


Question = Annotated[Union[SelectorQuestion, TextQuestion, ScaleQuestion], Field(discriminator='question_type')]


class Page(BaseModel):
    text: str | None = Field(None, min_length=1)
    questions: list[Question] = []

    @field_validator("questions")
    @classmethod
    def validate_questions(cls, v, info):
        uuids = set()
        for question in v:
            uuids.add(question.id)

        if len(v) != len(uuids):
            raise ValueError(FormError.SIMMILAR_ID_ERR.value)

        return v


class FormData(BaseModel):
    name: str = Field(min_length=1)
    pages: list[Page] = []

    @property
    def questions(self) -> list[Question]:
        questions = []
        for page in self.pages:
            questions.extend(page.questions)
        return questions


class Form(BaseModel):
    id: int
    data: FormData
