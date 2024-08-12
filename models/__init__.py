import pydantic


class BaseModel(pydantic.BaseModel):
    class Config:
        from_attributes = True


from .settings import settings
from .user import *
from .form import *
