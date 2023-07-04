import json


class TaskObject:
    def __init__(self, entity_id: int, record_id: int, foo: str, bar: str):
        self.entity_id = entity_id
        self.record_id = record_id
        self.foo = foo
        self.bar = bar


class TaskObjectEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, TaskObject):
            return {
                "foo": o.foo,
                "bar": o.bar,
            }
        return super().default(o)
