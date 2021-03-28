from enum import Enum
from typing import *

from pydantic import BaseModel


class CrutchStatus(str, Enum):
    ok = 'ok'
    emergency = 'emergency'
    error = 'error'
    offline = 'offline'

class ServerStatus(str, Enum):
    ok = 'ok'
    error = 'error'

class Loc(BaseModel):
    latitude: float
    longitude: float

class CrutchSettings(BaseModel):
    home_loc: Optional[Loc] = None
    phone: Optional[str] = None
    password: Optional[str] = None