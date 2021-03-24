from fastapi import FastAPI
from loguru import logger

from .typing_ import *

# from pydantic import BaseModel
# from typing import Optional

app = FastAPI()


# Heartbeat

class HeatbeatData(BaseModel):
    uuid: str
    status: DemoboardStatus
    loc: Optional[Loc]

@app.post("/demoboard/heatbeat")
def heatbeat(data: HeatbeatData):
    logger.debug(f"Recv heatbeat: {data}")

    return {'status': ServerStatus.ok}


# Emergency

class EmergencyData(BaseModel):
    uuid: str
    loc: Optional[Loc]

@app.post("/demoboard/emergency")
def emergency(data: EmergencyData):

    logger.debug(f"Recv emergency: {data}")
    get_demoboard(data.uuid)
    return {'status': ServerStatus.ok}


# GetSettings

class SettingsData(BaseModel):
    status: ServerStatus
    settings: DemoboardSettings

@app.get("/demoboard/get_settings/{uuid}")
def get_settings(uuid: str):
    logger.debug(f"Recv get settings req from {uuid}")
    return SettingsData(status=ServerStatus.ok, phone='12345678', home_addr=Loc())