import datetime as dt
import json
import secrets
from typing import Any, List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from errors import ParameterError

Base = so.declarative_base()
KEY_LENGTH: int = 16


class Entity(Base):
    """Модель отслеживаемой сущности"""

    __tablename__: str = "test_table"
    relevant_atributes: List[str] = [
        "foo",
        "bar",
    ]  # при добавлении новых атрибутов необходимо обновить этот список

    entity_id: so.Mapped[int] = so.mapped_column("id", sa.Integer)
    record_id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    foo: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    bar: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)

    def __init__(
        self,
        entity_id: int,
        foo: str,
        bar: str,
        record_id: Optional[int] = None,
    ) -> None:
        """
        Создает новую отслеживаемую сущность.

        Args:
            entity_id (int): Идентификатор сущности.
            foo (str): Значение атрибута "foo".
            bar (str): Значение атрибута "bar".
            record_id (int, optional): Идентификатор записи. Если не указан, будет сгенерирован автоматически. (default: None)
        """
        self.entity_id = entity_id
        self.foo = foo
        self.bar = bar
        if record_id is not None:
            self.record_id = record_id


class ApiKey(Base):
    __tablename__: str = "api_keys"

    api_key_id: so.Mapped[int] = so.mapped_column(
        "id", sa.Integer, primary_key=True
    )
    name: so.Mapped[str] = so.mapped_column(sa.String(255))
    description: so.Mapped[str] = so.mapped_column(sa.String(500))
    created_at: so.Mapped[dt.datetime] = so.mapped_column(
        sa.DateTime, default=dt.datetime.now()
    )
    valid_until: so.Mapped[dt.datetime] = so.mapped_column(
        sa.DateTime,
        default=dt.datetime.now().replace(month=dt.datetime.now().month + 1),
    )
    key: so.Mapped[str] = so.mapped_column(sa.String(KEY_LENGTH * 2))

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        created_at: Optional[dt.datetime] = None,
        valid_until: Optional[dt.datetime] = None,
    ) -> None:
        """
        Создает новый API ключ.

        Args:
            name (str): Имя ключа.
            description (str, optional): Описание ключа. (default: None)
            created_at (dt.datetime, optional): Дата и время создания ключа. Если не указано, используется текущее время. (default: None)
            valid_until (dt.datetime, optional): Дата и время истечения срока действия ключа. Если не указано, используется текущая дата с увеличением месяца на 1. (default: None)
        """
        self.name = name
        self.description = description if description else ""
        if created_at:
            self.created_at = created_at
        if valid_until:
            self.valid_until = valid_until

        self.key = ApiKey._generate_api_key()

    def is_valid(self) -> bool:
        """
        Проверяет, является ли ключ действительным (не истек срок действия).

        Returns:
            bool: True, если ключ действителен, иначе False.
        """
        return self.valid_until > dt.datetime.now()

    @staticmethod
    def _generate_api_key() -> str:
        """
        Генерирует новый API ключ.

        Returns:
            str: Сгенерированный API ключ.
        """
        return secrets.token_hex(KEY_LENGTH)


class Patch:
    """Объект для возврата в формате JSON Patch"""

    # полный список
    # _SUPPORTED_OPERATIONS = ["add", "remove", "replace", "move", "copy", "test"] # noqa: E501

    # список допустимых в данной задаче
    _SUPPORTED_OPERATIONS: List[str] = ["add", "replace"]

    def __init__(
        self,
        operation: str = "replace",
        path: Optional[str] = None,
        value: Any = None,
    ) -> None:
        """
        Создает объект для возврата в формате JSON Patch.

        Args:
            operation (str, optional): Операция патча. Допустимые значения: "replace" (замена значения) или "add" (добавление значения). (default: "replace")
            path (str, optional): Путь к элементу, который будет изменен или добавлен. (default: None)
            value (Any, optional): Значение, которое будет установлено. (default: None)

        Raises:
            ParameterError: Если указана неподдерживаемая операция.
        """
        if operation not in self._SUPPORTED_OPERATIONS:
            raise ParameterError(
                f"Unsupported operation: {operation}. Supported operations: {self._SUPPORTED_OPERATIONS}"  # noqa: E501
            )
        self.operation = operation
        self.path = path
        self.value = value


class EntityEncoder(json.JSONEncoder):
    def default(self, o: Entity) -> Any:
        """
        Преобразует объект Entity в JSON-представление.

        Args:
            o (Entity): Объект Entity для преобразования.

        Returns:
            Any: JSON-представление объекта Entity.
        """
        if isinstance(o, Entity):
            return {
                "foo": o.foo,
                "bar": o.bar,
            }
        return super().default(o)


class PatchEncoder(json.JSONEncoder):
    def default(self, o: Patch) -> Any:
        """
        Преобразует объект Patch в JSON-представление.

        Args:
            o (Patch): Объект Patch для преобразования.

        Returns:
            Any: JSON-представление объекта Patch.
        """
        if isinstance(o, Patch):
            return {
                "op": o.operation,
                "path": o.path,
                "value": o.value,
            }
        return super().default(o)


class ApiKeyEncoder(json.JSONEncoder):
    def default(self, o: ApiKey) -> Any:
        """
        Преобразует объект ApiKey в JSON-представление.

        Args:
            o (ApiKey): Объект ApiKey для преобразования.

        Returns:
            Any: JSON-представление объекта ApiKey.
        """
        if isinstance(o, ApiKey):
            return {
                "name": o.name,
                "description": o.description,
                "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "valid_until": o.valid_until.strftime("%Y-%m-%d %H:%M:%S"),
                "key": o.key,
            }
        return super().default(o)
