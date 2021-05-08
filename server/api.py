from typing import Optional

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from server.core import get_crutch_obj, register_crutch, get_crutch_uuid
from server.typing_ import CrutchStatus, CrutchSettings, Loc

app = FastAPI(
    title="SmartCrutch API Docs",
    description="守护者云拐杖(SmartCrutch-v4)API文档",
    version="0.3"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"code": 100, "msg": str(exc)})
    )



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
    #### Description
    拐杖心跳包，每隔**5秒**发送一次

    #### Request
    - uuid: 拐杖uuid
    - status: 拐杖状态码:
        - 'ok': 正常
        - 'emergency': 摔倒
        - 'error': 错误
        - 'offline': 离线，**内部使用，不可通过Api设置**
    - loc: *可选项*，拐杖位置信息
        - latitude: 纬度
        - longitude: 经度

    #### Response
    - code: 返回值:
        - 0: 成功
        - 1: 拐杖未注册
    - msg: 返回值信息
    """

    logger.debug(f"Recv heartbeat: {data}")

    c = get_crutch_obj(data.uuid)

    # TODO: Handle crutch-not-registered exception

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
    settings: Optional[CrutchSettings]

@app.get("/demoboard/get_settings/{uuid}", response_model=GetsettingsOut)
def get_settings(uuid: str):
    """
    #### Description
    获取拐杖设置信息
    在拐杖启动时请求，若uuid不存在则自动注册

    #### Request
    - uuid: 拐杖uuid

    #### Response
    - code: 返回值:
        - 0: 成功
    - msg: 返回值信息
    - settings: 设置信息
        - phone: *可选项*，电话号码
        - password: *可选项*，App登录密码
        - home: *可选项*，家庭住址
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
    """
    #### Description
    绑定拐杖到App账号，App注册时调用

    #### Request
    - uuid: 拐杖uuid
    - username: 用户名，不可为空
    - password: 密码，不可为空

    #### Response
    - code: 返回值:
        - 0: 成功
        - 1: 拐杖uuid未注册
        - 2: 拐杖uuid已绑定账号
        - 3: 密码不可为空
        - 4: 用户名不可为空
        - 5: 用户名已使用
    - msg: 返回值信息
    """

    logger.debug(f"Recv register req: {data}")

    c = get_crutch_obj(data.uuid)
    if not c:
        logger.warning(f"Req trying to bind a unregistered crutch: {data.uuid}")
        return BindOut(code=1, msg='crutch has not been registered')

    if c.username:
        logger.warning(f"Req trying to bind a binded crutch: {data}")
        return BindOut(code=2, msg='crutch has been binded')

    if not data.password:
        logger.warning(f"Req trying to bind crutch without password: {data}")
        return BindOut(code=3, msg='password should not be empty')

    if not data.username:
        logger.warning(f"Req trying to bind crutch without username: {data}")
        return BindOut(code=4, msg='username should not be empty')

    if get_crutch_uuid(data.username):
        logger.warning(f"Req trying to bind a crutch to a occupied username: {data.username}")
        return BindOut(code=5, msg='username occupied')


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
    """
    #### Description
    获取拐杖uuid，App登录时调用

    #### Request
    - username: 用户名，不可为空
    - password: 密码，不可为空

    #### Response
    - code: 返回值:
        - 0: 成功
        - 1: 用户名不存在
        - 2: 密码错误
    - msg: 返回值信息
    - uuid: 拐杖uuid
    """

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
    """
    #### Description
    绑定拐杖到App账号，App注册时调用

    #### Request
    - uuid: 拐杖uuid
    - settings: 拐杖设置信息
        - phone: *可选项*，电话号码
        - password: App登录密码，不可为空
        - home: *可选项*，家庭住址

    #### Response
    - code: 返回值:
        - 0: 成功
        - 1: 无效的uuid
        - 2: 密码不可为空
    - msg: 返回值信息
    """

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
    """
    #### Description
    获取拐杖设置信息，类似 `demoboard/get_settings`，但uuid不存在不会自动注册

    #### Request
    - uuid: 拐杖uuid

    #### Response
    - code: 返回值:
        - 0: 成功
        - 1: 无效的uuid
    - msg: 返回值信息
    - settings: 设置信息
        - phone: *可选项*，电话号码
        - password: App登录密码
        - home: *可选项*，家庭住址
    """
    logger.debug(f"Recv get settings req from app: uuid={uuid}")
    c = get_crutch_obj(uuid)

    if not c:
        logger.warning(f"Got invalid uuid: {uuid}")
        return AppGetsettingsOut(code=1, msg='invalid uuid')

    return AppGetsettingsOut(code=0, msg='success', settings=c.settings)



# Get status

class GetStatusOut(BaseModel):
    code: int
    msg: str
    status: Optional[CrutchStatus]

@app.get("/app/get_status/{uuid}", response_model=GetStatusOut)
def get_status(uuid: str):
    """
    #### Description
    获取拐杖状态信息

    #### Request
    - uuid: 拐杖uuid

    #### Response
    - code: 返回值:
        - 0: 成功
        - 1: 无效的uuid
    - msg: 返回值信息
    - status: 拐杖状态码:
        - 'ok': 正常
        - 'emergency': 摔倒
        - 'error': 错误
        - 'offline': 离线
    """

    c = get_crutch_obj(uuid)

    if not c:
        logger.warning(f"Got invalid uuid: {uuid}")
        return UpdatesettingsOut(code=1, msg='invalid uuid')
    return GetStatusOut(code=0, msg='success', status=c.status)



# Get loc

class GetLocOut(BaseModel):
    code: int
    msg: str
    loc: Optional[Loc]

@app.get("/app/get_loc/{uuid}", response_model=GetLocOut)
def get_loc(uuid: str):
    """
    #### Description
    获取拐杖状态信息

    #### Request
    - uuid: 拐杖uuid

    #### Response
    - code: 返回值:
        - 0: 成功
        - 1: 无效的uuid
    - msg: 返回值信息
    - loc: *可选项*，拐杖位置信息
        - latitude: 纬度
        - longitude: 经度
    """

    c = get_crutch_obj(uuid)

    if not c:
        logger.warning(f"Got invalid uuid: {uuid}")
        return UpdatesettingsOut(code=1, msg='invalid uuid')
    return GetLocOut(code=0, msg='success', loc=c.loc)