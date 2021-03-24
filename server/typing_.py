from enum import Enum
from pydantic import BaseModel
from typing import Optional

class DemoboardStatus(str, Enum):
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

class DemoboardSettings(BaseModel):
    home_loc: Optional[Loc] = None
    phone: Optional[str]
    account: str
    password: str
