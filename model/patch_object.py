import json


class Patch:
    def __init__(self, op="replace", path=None, value=None):
        self.op = op
        self.path = path
        self.value = value


class PatchEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Patch):
            return {
                "op": o.op,
                "path": o.path,
                "value": o.value,
            }
        return super().default(o)
