from typing import Optional

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

from server.core import get_crutch_obj, register_crutch, get_crutch_uuid
from server.typing_ import CrutchStatus, ServerStatus, CrutchSettings, Loc

app = FastAPI()

# ============ Crutch ============

# Heartbeat

class HeatbeatData(BaseModel):
    uuid: str
    status: CrutchStatus
    loc: Optional[Loc]

@app.post("/demoboard/heatbeat")
def heatbeat(data: HeatbeatData):
    logger.debug(f"Recv heatbeat: {data}")

    c = get_crutch_obj(data.uuid)

    # TODO: Handle crutch-not-registered exceptation

    c.status, c.loc = data.status, data.loc

    return {'status': ServerStatus.ok}


# Emergency

class EmergencyData(BaseModel):
    uuid: str
    loc: Optional[Loc]

@app.post("/demoboard/emergency")
def emergency(data: EmergencyData):

    logger.debug(f"Recv emergency: {data}")
    return {'status': ServerStatus.ok}


# GetSettings

class SettingsData(BaseModel):
    status: ServerStatus
    settings: CrutchSettings

@app.get("/demoboard/get_settings/{uuid}")
def get_settings(uuid: str):
    logger.debug(f"Recv get settings req from {uuid}")
    c = get_crutch_obj(uuid)
    if not c:
        c = register_crutch(uuid)
    return c.settings



# ============ Android app ============

# # Phonenumber
#
# class PhonenumberData(BaseModel):
#    phonenumber: str
#
# @app.post("/app/phonenumber")
# def Phonenumber(data: PhonenumberData):
#
#    return PhonenumberData()
#
#
# # Login
#
# class LoginData(BaseModel):
#    username: str
#    password: str
#    status: str
#    token: str
#    error_msg: str
#
# @app.post("/app/login")
# def Login(data: LoginData):
#
#    return LoginData()
#
#
#
# # Register
#
# class RegisterData(BaseModel):
#    status: str
#
# @app.post("/app/register")
# def Register(data: RegisterData):
#     pass
#
# @app.post("/app/update_settings")
# def update_settings