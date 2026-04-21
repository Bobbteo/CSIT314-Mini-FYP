import sqlite3
from fundraising_system.config import DB_NAME

class DBHelper:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn