import pydantic


class BaseModel(pydantic.BaseModel):
    class Config:
        orm_mode = True


from .settings import settings
from .user import *
