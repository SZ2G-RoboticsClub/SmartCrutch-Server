import os
import sqlite3
from typing import Optional

from loguru import logger

get_relative_path = lambda p: os.path.join(os.path.dirname(__file__), p)

class DataBase(object):
    def __init__(self):
        logger.info("Connecting database...")

        if os.path.exists(get_relative_path('../data/data.db')):
            is_init = True
        else:
            is_init = False

        self.conn = sqlite3.connect(get_relative_path('../data/data.db'), check_same_thread=False)
        self.cursor = self.conn.cursor()

        if not is_init:
            self.cursor.execute("CREATE TABLE settings (uuid text, username text, data json);")

    def __del__(self):
        logger.info("Disconnecting database...")
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    # def read(self, uuid: str):
    #     self.cursor.execute(f"SELECT * FROM settings WHERE uuid='{uuid}';")
    #     result = self.cursor.fetchall()
    #     return result[0][1] if result else None

    def create(self, uuid: str):
        self.cursor.execute('INSERT INTO settings VALUES (?, ?, ?);', (uuid, None, None))
        self.conn.commit()

    def update_settings(self, uuid: str, data: str):
        self.cursor.execute('UPDATE settings SET data = ? WHERE uuid = ?;', (data, uuid))
        self.conn.commit()

    def update_username(self, uuid: str, username: str):
        self.cursor.execute('UPDATE settings SET username = ? WHERE uuid = ?;', (username, uuid))
        self.conn.commit()

    # def update_image(self, uuid: str, image: Optional[image]):
    #     self.cursor.execute('UPDATE settings SET image = ? WHERE uuid = ?;', (image, uuid))
    #     self.conn.commit()

    def read_all(self):
        self.cursor.execute('SELECT * FROM settings;')
        return self.cursor.fetchall()


