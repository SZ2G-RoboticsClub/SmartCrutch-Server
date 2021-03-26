from time import time

from server.database import db
from server.typing_ import *

class Crutch(object):

    OFFLINE_TIME_THRESHOLD: float = 8.0

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __init__(self, uuid: str, settings: Optional[str] = None):
        self.uuid = uuid
        self.status = CrutchStatus.offline
        self.loc: Optional[Loc] = None
        self.last_conn_time = 0
        self.settings = CrutchSettings()

        if settings:
            self.settings.parse_raw(settings)

    def update_status(self, status: CrutchStatus):
        self.last_conn_time = time()
        self.status = status

    def get_status(self) -> CrutchStatus:
        if self.status == CrutchStatus.ok and time() - self.last_conn_time > self.OFFLINE_TIME_THRESHOLD:
            return CrutchStatus.offline
        return self.status

    def update_settings(self, settings: CrutchSettings):
        self.settings = settings
        db.write(self.uuid, settings.dict())

crutch_obj_list: List[Crutch]

def load_data():
    global crutch_obj_list
    crutch_obj_list = [Crutch(uuid, settings) for uuid, settings in db.read_all()]

def get_crutch_obj(uuid: str):
    try:
        idx = crutch_obj_list.index(Crutch(uuid))
    except ValueError:
        ret = Crutch(uuid)
        crutch_obj_list.append(ret)
        idx = -1
    return crutch_obj_list[idx]