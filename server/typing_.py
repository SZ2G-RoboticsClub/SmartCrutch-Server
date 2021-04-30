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

class CrutchSettings(BaseModel):
    """
    - home_loc: *可选项*，家庭地址
        - latitude: 纬度
        - longitude: 经度
    - phone:
    - password:
    """
    # home_loc: Optional[Loc] = None
    phone: Optional[str] = None
    password: Optional[str] = None

class image(BaseModel):
    image: str