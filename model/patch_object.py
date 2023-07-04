import json


class PatchObject:
    def __init__(self, op="patch", path=None, value=None):
        self.op = op
        self.path = path
        self.value = value


class PatchObjectEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, PatchObject):
            return {
                "op": o.op,
                "path": o.path,
                "value": o.value,
            }
        return super().default(o)
