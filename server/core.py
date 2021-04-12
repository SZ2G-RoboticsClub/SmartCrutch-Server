from time import time
from typing import Optional, List

from loguru import logger

from server.database import DataBase
from server.typing_ import CrutchStatus, Loc, CrutchSettings


class Crutch(object):
    OFFLINE_TIME_THRESHOLD: float = 8.0

    def __eq__(self, other):
        return self.uuid == other.uuid if self.uuid else self.username == other.username

    def __init__(self, uuid: Optional[str] = None,
                 username: Optional[str] = None,
                 settings: Optional[str] = None):

        assert uuid or username, "Crutch instance must be initialized with uuid or account!"

        self.uuid = uuid
        self.username = username

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


def get_crutch_uuid(username: str):
    try:
        idx = crutch_obj_list.index(Crutch(username=username))
    except ValueError:
        logger.warning(f"Crutch data not exist: Username='{username}'")
        return None
    return crutch_obj_list[idx].uuid


def get_crutch_obj(uuid: str):
    try:
        idx = crutch_obj_list.index(Crutch(uuid=uuid))
    except ValueError:
        logger.warning(f"Crutch data not exist: UUID='{uuid}'")
        return None
    return crutch_obj_list[idx]


def register_crutch(uuid: str) -> Optional[Crutch]:
    """
    Register a crutch to database.
    :param uuid: crutch UUID
    :return: crutch obj if succeeded, otherwise return None
    """
    if get_crutch_obj(uuid):
        logger.warning(f"Crutch (UUID='{uuid}) has already been registered.")
        return None

    db.create(uuid, None, CrutchSettings().json())
    crutch_obj_list.append(Crutch(uuid))

    logger.info(f"Crutch registered: UUID = {uuid}")
    return crutch_obj_list[-1]


def bind_crutch(crutch_obj: Crutch, username: str) -> bool:
    if get_crutch_uuid(username):
        logger.warning(f"Username '{username}' has already been occupied.")
        return False
    crutch_obj.username = username
    return True
