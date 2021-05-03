from time import time
from typing import Optional, List

from loguru import logger

from server.database import DataBase
from server.typing_ import CrutchStatus, Loc, CrutchSettings, Falltime


class Crutch(object):

    # If the time delta between crutch's last heartbeat and now exceeds the threshold,
    # judge the crutch is offline.
    # ** THE THRESHOLD SHOULD BE LONGER THAN THE HEARTBEAT INTERVAL SET ON THE DEMOBOARD **
    OFFLINE_TIME_THRESHOLD: float = 8.0

    def __eq__(self, other):
        # For finding crutch obj with uuid or username
        return self.uuid == other.uuid or (self.username and self.username == other.username)

    def __init__(self, uuid: Optional[str] = None,
                 username: Optional[str] = None,
                 settings: Optional[str] = None):

        assert uuid or username, "Crutch instance must be initialized with uuid or account!"

        self.uuid = uuid
        self._username = username

        self._status = CrutchStatus.offline
        self._last_conn_time = 0

        self.loc: Optional[Loc] = None
        self.falltime: Optional[Falltime] = None

        self._settings = CrutchSettings()

        if settings:
            self._settings = CrutchSettings.parse_raw(settings)

    @property
    def settings(self) -> CrutchSettings:
        return self._settings

    @settings.setter
    def settings(self, settings):
        self._settings = settings
        db.update_settings(self.uuid, self.settings.json())

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, username):
        self._username = username
        db.update_username(self.uuid, self.username)

    @property
    def status(self) -> CrutchStatus:
        if self._status == CrutchStatus.ok and time() - self._last_conn_time > self.OFFLINE_TIME_THRESHOLD:

            # The time delta between crutch's last connection and now
            # exceeds OFFLINE_TIME_THRESHOLD, return Offline status
            return CrutchStatus.offline

        return self._status

    @status.setter
    def status(self, status: CrutchStatus):
        self._last_conn_time = time()
        self._status = status


# Crutch obj list, the crutch instances are maintained in the list while running
crutch_obj_list: List[Crutch]

# database instance
db: DataBase


def load_database():
    """
    **INTERNAL FUNCTION**
    Load all crutch obj from database. Being called automatically when server initializing.
    """
    global crutch_obj_list, db
    db = DataBase()
    crutch_obj_list = [Crutch(uuid, username, settings) for uuid, username, settings in db.read_all()]


def get_crutch_uuid(username: str) -> Optional[str]:
    """
    Get a crutch uuid with username. Mainly used for app login.
    :param username: the username crutch bound
    :return: uuid if the crutch is found, otherwise return None
    """
    try:
        idx = crutch_obj_list.index(Crutch(username=username))
    except ValueError:
        logger.debug(f"Crutch data not exist: Username='{username}'")
        return None
    return crutch_obj_list[idx].uuid


def get_crutch_obj(uuid: str) -> Optional[Crutch]:
    """
    Get a registered crutch obj with uuid.
    :param uuid: cruch UUID
    :return: crutch obj if the obj exist, otherwise return None
    """
    try:
        idx = crutch_obj_list.index(Crutch(uuid=uuid))
    except ValueError:
        logger.debug(f"Crutch data not exist: UUID='{uuid}'")
        return None
    return crutch_obj_list[idx]


def register_crutch(uuid: str) -> Optional[Crutch]:
    """
    Register a crutch in database.
    :param uuid: crutch UUID
    :return: crutch obj if succeeded, otherwise return None
    """
    if get_crutch_obj(uuid):
        logger.warning(f"Crutch (UUID='{uuid}) has already been registered.")
        return None

    db.create(uuid)
    crutch_obj_list.append(Crutch(uuid))

    logger.info(f"Crutch registered: UUID = {uuid}")
    return crutch_obj_list[-1]