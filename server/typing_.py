from enum import Enum
from typing import *

from pydantic import BaseModel


class CrutchStatus(str, Enum):
    ok = 'ok'
    emergency = 'emergency'
    error = 'error'
    offline = 'offline'

class Loc(BaseModel):
    latitude: float
    longitude: float

class CrutchSettings(BaseModel):
    """
    - phone: *可选项*，紧急联系人电话号码
    - password: *可选项*，App登录密码
    - home: *可选项*，家庭住址
    """
    home: Optional[Loc] = None
    phone: Optional[str] = None
    password: Optional[str] = None