import pydantic
import re
from typing import Type, Optional


password_pattern = r"^(?=.*[a-z_])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&_])[A-Za-z\d@$!#%*?&_]{8,200}$"


class HttpError(Exception):
    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


class CreateUserScheme(pydantic.BaseModel):
    username: str
    password: str
    email: Optional[str]

    @pydantic.validator('username')
    def check_username(cls, value: str):
        if len(value) <= 1:
            raise ValueError('username is too short')
        if len(value) > 32:
            raise ValueError('username is too long')
        return value

    @pydantic.validator('password')
    def check_password(cls, value: str):
        if not re.search(password_pattern, value):
            raise ValueError('password is too easy')
        return value


class CreateAdvertisementScheme(pydantic.BaseModel):
    title: str
    description: str
    id_user: int

    @pydantic.validator('title')
    def check_title(cls, value: str):
        if value == "":
            raise ValueError('title is empty')
        if len(value) > 100:
            raise ValueError('title is too long')
        return value

    @pydantic.validator('description')
    def check_description(cls, value: str):
        if value == "":
            raise ValueError('description is empty')
        return value


def validate(val_data: dict, val_class: Type[CreateUserScheme] | Type[CreateAdvertisementScheme]):
    try:
        return val_class(**val_data).dict()
    except pydantic.ValidationError as error:
        raise HttpError(400, error.errors())
