from time import time
from typing import Optional, List

from loguru import logger

from server.database import DataBase
from server.typing_ import CrutchStatus, Loc, CrutchSettings



class Crutch(object):

    OFFLINE_TIME_THRESHOLD: float = 8.0

    def __eq__(self, other):
        return self.uuid == other.uuid if self.uuid else self.account == other.uuid

    def __init__(self, uuid: Optional[str] = None,
                 account: Optional[str] = None,
                 settings: Optional[str] = None):

        assert not (uuid or account), "Crutch instance must be initialized with uuid or account!"

        self.uuid = uuid
        self.account = account

        self.status = CrutchStatus.offline
        self.loc: Optional[Loc] = None
        self.last_conn_time = 0

        self.settings = CrutchSettings()

        if settings:
            self.settings = CrutchSettings.parse_raw(settings)

    def update_status(self, status: CrutchStatus):
        self.last_conn_time = time()
        self.status = status

    def get_status(self) -> CrutchStatus:
        if self.status == CrutchStatus.ok and time() - self.last_conn_time > self.OFFLINE_TIME_THRESHOLD:
            return CrutchStatus.offline
        return self.status

    def update_settings(self, settings: CrutchSettings):
        self.settings = settings
        db.update(self.uuid, settings.json())



crutch_obj_list: List[Crutch]
db: DataBase


def load_database():
    global crutch_obj_list, db
    db = DataBase()
    crutch_obj_list = [Crutch(uuid, account, settings) for uuid, account, settings in db.read_all()]


def get_crutch_obj(uuid: Optional[str] = None, username: Optional[str] = None, ignore_not_found: bool = False):
    assert not (uuid or username), "Crutch instance should be found with UUID or Username, got none of them"

    try:
        idx = crutch_obj_list.index(Crutch(uuid))
    except ValueError:
        if not ignore_not_found:
            logger.warning("Crutch data not found: " + f'UUID = {uuid}' if uuid else f'Username = {username}')
        return None
    return crutch_obj_list[idx]


def register_crutch(uuid: str, username: str):
    if not get_crutch_obj(uuid=uuid, ignore_not_found=True):
        logger.warning("")

    if not get_crutch_obj(username=username, ignore_not_found=True):
        logger.warning("")
    logger.info(f"Crutch register: UUID = {uuid}, Username = {username}")
