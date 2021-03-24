from .typing_ import *
from typing import List

from time import time

class Crutch(object):

    OFFLINE_TIME_THRESHOLD: float = 8.0

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __str__(self):
        return self.uuid

    def __init__(self, uuid: str):
        self.uuid = uuid
        self.status = CrutchStatus.offline
        self.loc: Optional[Loc] = None
        self.last_conn_time = 0
        self.settings = CrutchSettings()

    def update(self, status: CrutchStatus):
        self.last_conn_time = time()
        self.status = status

    def get_status(self) -> CrutchStatus:
        if self.status == CrutchStatus.ok and time() - self.last_conn_time > self.OFFLINE_TIME_THRESHOLD:
            return CrutchStatus.offline
        return self.status

    def update_settings(self, settings: CrutchSettings):
        self.settings = settings

    def load_settings(self, settings: dict):
        self.settings = CrutchSettings()

g_crutch: List[Crutch] = []

def get_crutch(uuid: str):
    idx = g_crutch.index(Crutch(uuid))
    if not idx:
        ret = Crutch(uuid)
        return g_crutch.append(ret)
    return g_crutch[idx]