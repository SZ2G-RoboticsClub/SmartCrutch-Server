import sqlite3
import os
from .main import g_crutch

class DataBase(object):
    def __init__(self):
        self.conn = sqlite3.connect('settings.db')
        self.cursor = self.conn.cursor()

    def init_settings(self):
        self.cursor.execute("CREATE TABLE settings (uuid CHARACTER(36), data json)")

