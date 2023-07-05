from abc import ABC, abstractmethod


class AbsConnection(ABC):
    """
    Интерфейс для работы с базой данных, вдохновленный заброшенным dbpy
    """

    def __init__(self, db_options=None):
        db_options = db_options or {}

        self._db_options = self.default_options()
        self._db_options.update(db_options)

        self._connection = None
        self.connect()

    def execute(self, query, args=None) -> list:
        """Выполняет запрос к базе данных"""
        self.ensure_connection()
        with self.cursor() as cursor:
            cursor.execute(query, args)
            rows = cursor.fetchall()
        return rows

    def default_options(self) -> dict:
        """Параметры по умолчанию для соединения с базой данных"""
        return {}

    @abstractmethod
    def connect(self):
        """Устанавливает соединение с базой данных"""

    def close(self):
        """Закрывает соединение с базой данных"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @abstractmethod
    def ensure_connection(self):
        """Проверяет доступность соединения с базой данных"""

    def cursor(self):
        """Возвращает курсор"""
        self.ensure_connection()
        cursor_type = self.cursor_type(is_dict=True)
        return self._connection.cursor(cursor_type)

    @abstractmethod
    def cursor_type(self, is_dict=True):
        """Возвращает класс SQL курсора"""

    def commit(self):
        """Фиксирует транзакцию"""
        self._connection.commit()
