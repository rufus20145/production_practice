import json

import sqlalchemy as sa
import sqlalchemy.orm as so

from errors import ParameterError

Base = so.declarative_base()


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
