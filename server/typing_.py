from enum import Enum
from typing import *

from pydantic import BaseModel, validator


class CrutchStatus(str, Enum):
    ok = 'ok'
    emergency = 'emergency'
    error = 'error'
    offline = 'offline'

class Loc(BaseModel):
    latitude: float
    longitude: float

class CrutchSettings(BaseModel):
    home_loc: Optional[Loc] = None
    phone: Optional[str] = None
    password: Optional[str] = None

    @validator('password')
    def _(cls, v):
        assert v, "password must not be empty"
        return v