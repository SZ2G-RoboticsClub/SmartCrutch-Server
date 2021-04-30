from time import time
from typing import Optional, List

from loguru import logger

from server.database import DataBase
from server.typing_ import CrutchStatus, Loc, CrutchSettings, CrutchImage


class Crutch(object):
    OFFLINE_TIME_THRESHOLD: float = 8.0

    def __eq__(self, other):
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

        self._settings = CrutchSettings()

        self._image = CrutchImage.offline

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
            return CrutchStatus.offline
        return self._status

    @status.setter
    def status(self, status: CrutchStatus):
        self._last_conn_time = time()
        self._status = status

    @property
    def img(self) -> CrutchImage:
        if self._img == CrutchImage.ok and time() - self._last_conn_time > self.OFFLINE_TIME_THRESHOLD:
            return CrutchImg.offline
        return self._img

    @image.setter
    def image(self, status: CrutchImage):
        self._last_conn_time = time()
        self._image = image


crutch_obj_list: List[Crutch]
db: DataBase


def load_database():
    global crutch_obj_list, db
    db = DataBase()
    crutch_obj_list = [Crutch(uuid, username, settings, image) for uuid, username, settings, image in db.read_all()]


def get_crutch_uuid(username: str) -> Optional[str]:
    try:
        idx = crutch_obj_list.index(Crutch(username=username))
    except ValueError:
        logger.debug(f"Crutch data not exist: Username='{username}'")
        return None
    return crutch_obj_list[idx].uuid


def get_crutch_obj(uuid: str) -> Optional[Crutch]:
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