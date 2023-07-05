"""
TODO module docstring 
"""
import json
import logging as log

from cdb.pymysql.connection import PyMySQLConnection
from model.patch_object import PatchObject, PatchObjectEncoder
from model.task_object import TaskObject, TaskObjectEncoder

DEFAULT_FILE = "connection_params.json"


class ChangeMonitor:
    """
    TODO class docstring
    """

    _max_record_id = 0
    _cache: "dict[int, TaskObject]" = {}

    def __init__(self, file_name=DEFAULT_FILE):
        with open(file=file_name, encoding="utf-8") as file:
            params = json.load(file)
        self._db = PyMySQLConnection(params)
        log.info("Connected to database")

    def get_initial_state(self) -> str:
        """
        TODO docstring
        """

        rows = self._db.execute(
            """
            SELECT t1.id, t1.record_id, t1.foo, t1.bar
            FROM test_table AS t1
            JOIN (
                SELECT id, MAX(record_id) AS max_record_id
                FROM test_table
                GROUP BY id
            ) AS t2
            ON t1.id = t2.id
            AND t1.record_id = t2.max_record_id
            ORDER BY id;
            """
        )
        for row in rows:
            if row["record_id"] > self._max_record_id:
                self._max_record_id = row["record_id"]
            entity = TaskObject(row["id"], row["record_id"], row["foo"], row["bar"])
            self._cache[entity.entity_id] = entity

        log.info("Max record id after initial state: %d", self._max_record_id)
        return json.dumps(self._cache, cls=TaskObjectEncoder)

    def get_update(self) -> str:
        """
        TODO docstring
        """
        result_list = []

        rows = self._db.execute(
            """
                SELECT id, record_id, foo, bar
                FROM test_table
                WHERE record_id > %s
                ORDER BY record_id;
                """,
            (self._max_record_id,),
        )
        for row in rows:
            if row["record_id"] > self._max_record_id:
                self._max_record_id = row["record_id"]

            new_obj = TaskObject(row["id"], row["record_id"], row["foo"], row["bar"])
            if new_obj.entity_id not in self._cache:
                self._cache[new_obj.entity_id] = new_obj
                result_list.append(
                    PatchObject(
                        op="add",
                        path=f"/{new_obj.entity_id}",
                        value=json.dumps(new_obj, cls=TaskObjectEncoder),
                    )
                )
            else:
                old_obj = self._cache[new_obj.entity_id]
                if new_obj.foo != old_obj.foo:
                    result_list.append(
                        PatchObject(
                            op="replace",
                            path=f"/{new_obj.entity_id}/foo",
                            value=new_obj.foo,
                        )
                    )
                if new_obj.bar != old_obj.bar:
                    result_list.append(
                        PatchObject(
                            op="replace",
                            path=f"/{new_obj.entity_id}/bar",
                            value=new_obj.bar,
                        )
                    )
        log.info("Max record id after patch: %d", self._max_record_id)
        return json.dumps(result_list, cls=PatchObjectEncoder)
