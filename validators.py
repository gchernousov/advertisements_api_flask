import pydantic
from typing import Type


class HttpError(Exception):

    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


class CreateUserScheme(pydantic.BaseModel):
    username: str
    password: str

    @pydantic.validator('username')
    def check_username(cls, value: str):
        if len(value) < 3:
            raise ValueError('username is too short')
        if len(value) > 32:
            raise ValueError('username is too long')
        return value

    @pydantic.validator('password')
    def check_password(cls, value: str):
        if len(value) < 5:
            raise ValueError('password is too short')
        return value


def validate(val_data: dict, val_class: Type[CreateUserScheme]):
    try:
        return val_class(**val_data).dict()
    except pydantic.ValidationError as error:
        raise HttpError(400, error.errors())