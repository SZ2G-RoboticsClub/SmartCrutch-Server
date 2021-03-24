from .typing_ import *
from typing import List

from time import time

class DemoBoard(object):

    OFFLINE_TIME_THRESHOLD: float = 8.0

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __str__(self):
        return self.uuid

    def __init__(self, uuid: str):
        self.uuid = uuid
        self.status = DemoboardStatus.offline
        self.loc: Optional[Loc] = None
        self.last_conn_time = 0
        self.settings = DemoboardSettings()

    def update(self, status: DemoboardStatus):
        self.last_conn_time = time()
        self.status = status

    def get_status(self) -> DemoboardStatus:
        if self.status == DemoboardStatus.ok and time() - self.last_conn_time > self.OFFLINE_TIME_THRESHOLD:
            return DemoboardStatus.offline
        return self.status

    def update_settings(self, settings: DemoboardSettings):
        self.settings = settings

    def load_settings(self, settings: dict):
        self.settings = DemoboardSettings()


g_demoboard: List[DemoBoard] = []

def get_demoboard(uuid: str):
    idx = g_demoboard.index(uuid)
    if not idx:
        ret = DemoBoard(uuid)
        return g_demoboard.append(ret)
    return g_demoboard[idx]