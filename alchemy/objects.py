from base import Base
from sqlalchemy import Column, Integer, String


class Entity(Base):
    __tablename__ = "test"

    entity_id = Column("id", Integer)
    record_id = Column("record_id", Integer, primary_key=True, autoincrement=True)
    foo = Column("foo", String(255), nullable=False)
    bar = Column("bar", String(255), nullable=False)

    def __init__(self, entity_id, foo, bar, record_id=None):
        self.entity_id = entity_id
        self.record_id = record_id
        self.foo = foo
        self.bar = bar
