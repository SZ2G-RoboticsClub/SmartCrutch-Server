from enum import Enum
from typing import *

from pydantic import BaseModel


class CrutchStatus(str, Enum):
    ok = 'ok' # ok
    emergency = 'emergency' # fell down
    error = 'error' # demoboard internal error
    offline = 'offline' # offline

class Loc(BaseModel):
    latitude: float
    longitude: float    

class Falltime(BaseModel):
    date: str
    time: str

class CrutchSettings(BaseModel):
    """
    - phone:
    - password:
    - home:家庭住址（str）
    """
    # home_loc: Optional[Loc] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    home: Optional[str] = None

