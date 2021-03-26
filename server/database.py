import os
import sqlite3

from loguru import logger

get_relative_path = lambda p: os.path.join(os.path.dirname(__file__), p)

class DataBase(object):
    def __init__(self):
        logger.info("Connecting database...")

        if os.path.exists(get_relative_path('../data/data.db')):
            is_init = True
        else:
            is_init = False

        self.conn = sqlite3.connect(get_relative_path('../data/data.db'))
        self.cursor = self.conn.cursor()

        if not is_init:
            self.cursor.execute("CREATE TABLE settings (uuid CHARACTER(36), data json);")

    def __del__(self):
        logger.info("Disconnecting database...")
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def read(self, uuid: str):
        self.cursor.execute(f"SELECT * FROM settings WHERE uuid='{uuid}';")
        result = self.cursor.fetchall()
        return result[0][1] if result else None

    def write(self, uuid: str, data: dict):
        if self.read(uuid):
            self.cursor.execute(f"""UPDATE settings SET data = "{data}";""")
        else:
            self.cursor.execute(f"""INSERT INTO settings VALUES ('{uuid}', "{data}");""")
        self.conn.commit()

    def read_all(self):
        self.cursor.execute(f"SELECT * FROM settings;")
        return self.cursor.fetchall()

db = DataBase()


