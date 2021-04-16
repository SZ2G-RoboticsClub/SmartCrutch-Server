from typing import Optional

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

from server.core import get_crutch_obj, register_crutch, get_crutch_uuid
from server.typing_ import CrutchStatus, CrutchSettings, Loc

app = FastAPI()



# ============ Crutch ============



# Heartbeat

class HeartbeatIn(BaseModel):
    uuid: str
    status: CrutchStatus
    loc: Optional[Loc]

class HeartbeatOut(BaseModel):
    code: int
    msg: str

@app.post("/demoboard/heartbeat", response_model=HeartbeatOut)
def heartbeat(data: HeartbeatIn):
    """
    ### Description
    拐杖心跳包，每隔**5秒**发送一次

    ### Request
    - uuid: 拐杖uuid
    - status: 拐杖状态码:
        - 'ok': 正常
        - 'emergency': 摔倒
        - 'error': 错误
        - ~~ 'offline': 离线，**内部使用，不可通过Api设置** ~~
    - loc: *可选项*，位置经纬度数据
        - latitude: 经度
        - longitude: 纬度

    ### Response
    - code: 返回值:
        - 0: 成功
        - 1: 拐杖未注册
    - msg: 返回值信息
    """

    logger.debug(f"Recv heartbeat: {data}")

    c = get_crutch_obj(data.uuid)

    # TODO: Handle crutch-not-registered exceptation

    if not c:
        return HeartbeatOut(code=1, msg='crutch has not been registered')

    c.status, c.loc = data.status, data.loc

    return HeartbeatOut(code=0, msg='success')



# # Emergency
#
# class EmergencyIn(BaseModel):
#     uuid: str
#     loc: Optional[Loc]
#
# class EmergencyOut(BaseModel):
#     code: int
#     msg: str
#
# @app.post("/demoboard/emergency", response_model=EmergencyOut)
# def emergency(data: EmergencyIn):
#
#     logger.debug(f"Recv emergency: {data}")
#     return EmergencyOut(code=0, msg='success')



# GetSettings

class GetsettingsOut(BaseModel):
    code: int
    msg: str
    settings: CrutchSettings

@app.get("/demoboard/get_settings/{uuid}", response_model=GetsettingsOut)
def get_settings(uuid: str):
    """
    ### Description
    获取拐杖设置信息
    在拐杖启动时请求，若uuid不存在则自动注册

    ### Request
    - uuid: 拐杖uuid

    ### Response
    - code: 返回值:
        - 0: 成功
    - msg: 返回值信息
    - settings: 设置信息
        - home_loc: *可选项*，家庭地址
            - latitude: 经度
            - longitude: 纬度
        - phone: *可选项*，电话号码
        - password: *可选项*，App登录密码
    """

    logger.debug(f"Recv get settings req from {uuid}")
    c = get_crutch_obj(uuid)
    if not c:
        c = register_crutch(uuid)
    return GetsettingsOut(code=0, msg='success', settings=c.settings)



# ============ Android app ============



# Bind

class BindIn(BaseModel):
    uuid: str
    username: str
    password: str

class BindOut(BaseModel):
    code: int
    msg: str

@app.post("/app/bind", response_model=BindOut)
def bind(data: BindIn):
    logger.debug(f"Recv register req: {data}")

    c = get_crutch_obj(data.uuid)
    if not c:
        logger.warning(f"Req trying to bind a unregistered crutch: {data.uuid}")
        return BindOut(code=1, msg='crutch has not been registered')

    if c.username:
        logger.warning(f"Req trying to bind a binded crutch: {data}")
        return BindOut(code=2, msg='crutch has been binded')

    if get_crutch_uuid(data.username):
        logger.warning(f"Req trying to bind a crutch to a occupied username: {data.username}")
        return BindOut(code=3, msg='username occupied')

    if not data.password:
        logger.warning("Req trying to bind crutch without password")
        return BindOut(code=4, msg='password should not be empty')

    c.settings = CrutchSettings(password=data.password)
    c.username = data.username

    logger.info(f"Crutch binded: {data}")
    return BindOut(code=0, msg='success')



# Login

class LoginIn(BaseModel):
    username: str
    password: str

class LoginOut(BaseModel):
    code: int
    msg: str
    uuid: Optional[str] = None

@app.post("/app/login", response_model=LoginOut)
def login(data: LoginIn):
    logger.debug(f"Recv login req: {data}")

    uuid = get_crutch_uuid(data.username)
    if not uuid:
        logger.warning(f"Username not exist: {data.username}")
        return LoginOut(code=1, msg='username not exist')

    real_pwd = get_crutch_obj(uuid).settings.password
    if real_pwd != data.password:
        logger.warning(f"Password incorrect: username={data.username}, password={data.password}, got {real_pwd}.")
        return LoginOut(code=2, msg='password incorrect')

    logger.info(f"App logined: username={data.username}, uuid={uuid}")
    return LoginOut(code=0, msg='success', uuid=uuid)



# Update settings

class UpdatesettingsIn(BaseModel):
    uuid: str
    settings: CrutchSettings

class UpdatesettingsOut(BaseModel):
    code: int
    msg: str

@app.post("/app/update_settings", response_model=UpdatesettingsOut)
def update_settings(data: UpdatesettingsIn):
    logger.debug(f"Recv update settings req: {data}")

    c = get_crutch_obj(data.uuid)
    if not c:
        logger.warning(f"Got invalid uuid: {data.uuid}")
        return UpdatesettingsOut(code=1, msg='invalid uuid')

    if not data.settings.password:
        logger.warning(f"Got empty password: {data}")
        return UpdatesettingsOut(code=2, msg='password should not be empty')

    c.settings = data.settings

    logger.info(f"Settings updated: uuid={data.uuid}, settings={data.settings}")
    return UpdatesettingsOut(code=0, msg='success')



# AppGetSettings

class AppGetsettingsOut(BaseModel):
    code: int
    msg: str
    settings: Optional[CrutchSettings]

@app.get("/app/get_settings/{uuid}", response_model=AppGetsettingsOut)
def app_get_settings(uuid: str):
    logger.debug(f"Recv get settings req from app: uuid={uuid}")
    c = get_crutch_obj(uuid)

    if not c:
        logger.warning(f"Got invalid uuid: {uuid}")
        return AppGetsettingsOut(code=1, msg='invalid uuid')

    return AppGetsettingsOut(code=0, msg='success', settings=c.settings)