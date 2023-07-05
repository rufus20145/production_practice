import pymysql

from cdb.connection import AbsConnection


class PyMySQLConnection(AbsConnection):
    """Реализация подключения к базе данных MySQL"""

    def default_options(self):
        return {
            "port": 3306,
            "host": "localhost",
            "user": "test",
            "password": "test",
            "database": "test",
            "use_unicode": True,
            "charset": "utf8",
            "autocommit": True,
        }

    def connect(self):
        self.close()
        self._connection = pymysql.connect(**self._db_options)

    def ensure_connection(self):
        if self._connection:
            self._connection.ping(reconnect=True)
        else:
            self.connect()

    def cursor_type(self, is_dict=True):
        if is_dict:
            return pymysql.cursors.DictCursor
        return pymysql.cursors.Cursor
