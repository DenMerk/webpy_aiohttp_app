import pydantic
from typing import Optional, Type


class CreateAdv(pydantic.BaseModel):
    title: str
    description: str
    author: str

    @pydantic.validator('title')
    def validate_title(cls, value):
        if len(value) == 0:
            raise ValueError('The adv must contain a title')
        return value


class PatchAdv(pydantic.BaseModel):
    title: Optional[str]
    description: Optional[str]
    author: Optional[str]

    @pydantic.validator('title')
    def validate_title(cls, value):
        if len(value) == 0:
            raise ValueError('The adv must contain a title')
        return value


VALIDATION_CLASS = Type[CreateAdv] | Type[PatchAdv]
