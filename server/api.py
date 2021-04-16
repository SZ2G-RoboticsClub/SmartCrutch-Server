from typing import Optional

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel, ValidationError

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
    logger.debug(f"Recv heartbeat: {data}")

    c = get_crutch_obj(data.uuid)

    # TODO: Handle crutch-not-registered exceptation

    if not c:
        return HeartbeatOut(code=1, msg='crutch has not been registered')

    c.status, c.loc = data.status, data.loc

    return HeartbeatOut(code=0, msg='success')



# Emergency

class EmergencyIn(BaseModel):
    uuid: str
    loc: Optional[Loc]

class EmergencyOut(BaseModel):
    code: int
    msg: str

@app.post("/demoboard/emergency", response_model=EmergencyOut)
def emergency(data: EmergencyIn):

    logger.debug(f"Recv emergency: {data}")
    return EmergencyOut(code=0, msg='success')



# GetSettings

class GetsettingsOut(BaseModel):
    code: int
    msg: str
    settings: CrutchSettings

@app.get("/demoboard/get_settings/{uuid}", response_model=GetsettingsOut)
def get_settings(uuid: str):
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

    c.update_settings(CrutchSettings(password=data.password))
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
def login(data: UpdatesettingsIn):
    logger.debug(f"Recv update settings req: {data}")

    c = get_crutch_obj(data.uuid)
    if not c:
        logger.warning(f"Got invalid uuid: {data.uuid}")
        return UpdatesettingsOut(code=1, msg='crutch has not been registered')

    try:
        c.update_settings(CrutchSettings)
    except ValidationError:
        logger.warning(f"Got invalid settings: {data.settings}")
        return UpdatesettingsOut(code=1, msg='crutch has not been registered')

    logger.info(f"Settings updated: uuid={data.uuid}, settings={data.settings}")
    return UpdatesettingsOut(code=0, msg='success')