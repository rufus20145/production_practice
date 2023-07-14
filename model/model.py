import datetime as dt
import json
import secrets

import sqlalchemy as sa
import sqlalchemy.orm as so

from errors import ParameterError

Base = so.declarative_base()
KEY_LENGTH: int = 16


class Entity(Base):
    """Модель отслеживаемой сущности"""

    __tablename__ = "test_table"
    relevant_atributes = [
        "foo",
        "bar",
    ]  # при добавлении новых атрибутов необходимо обновить этот список

    entity_id: so.Mapped[int] = so.mapped_column("id", sa.Integer)
    record_id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    foo: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    bar: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)

    def __init__(self, entity_id, foo, bar, record_id=None):
        self.entity_id = entity_id
        self.record_id = record_id
        self.foo = foo
        self.bar = bar


class ApiKey(Base):
    __tablename__ = "api_keys"

    api_key_id: so.Mapped[int] = so.mapped_column(
        "id", sa.Integer, primary_key=True
    )
    name: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    description: so.Mapped[str] = so.mapped_column(
        sa.String(500), nullable=False
    )
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
        description: str,
        created_at: dt.datetime = None,
        valid_until: dt.datetime = None,
    ):
        self.name = name
        self.description = description
        self.created_at = created_at if created_at else dt.datetime.now()
        self.valid_until = (
            valid_until
            if valid_until
            else dt.datetime.now().replace(month=dt.datetime.now().month)
        )

        self.key = self._generate_api_key()

    def is_valid(self) -> bool:
        return self.valid_until > dt.datetime.now()

    @staticmethod
    def _generate_api_key():
        return secrets.token_hex(KEY_LENGTH)


class Patch:
    """Объект для возврата в формате JSON Patch"""

    # полный список
    # _SUPPORTED_OPERATIONS = ["add", "remove", "replace", "move", "copy", "test"] # noqa: E501

    # список допустимых в данной задаче
    _SUPPORTED_OPERATIONS = ["add", "replace"]

    def __init__(self, operation="replace", path=None, value=None):
        if operation not in self._SUPPORTED_OPERATIONS:
            raise ParameterError(
                f"""Unsupported operation: {operation}.
                Supported operations: {self._SUPPORTED_OPERATIONS}"""
            )
        self.operation = operation
        self.path = path
        self.value = value


class EntityEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Entity):
            return {
                "foo": o.foo,
                "bar": o.bar,
            }
        return super().default(o)


class PatchEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Patch):
            return {
                "op": o.operation,
                "path": o.path,
                "value": o.value,
            }
        return super().default(o)


class ApiKeyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ApiKey):
            return {
                "name": o.name,
                "description": o.description,
                "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "valid_until": o.valid_until.strftime("%Y-%m-%d %H:%M:%S"),
                "key": o.key,
            }
        return super().default(o)
