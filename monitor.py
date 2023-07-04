"""
TODO module docstring 
"""
import json
import logging as log

import pymysql

from model.patch_object import PatchObject, PatchObjectEncoder
from model.task_object import TaskObject, TaskObjectEncoder

FILE = "connection_params.json"


class ChangeMonitor:
    """
    TODO class docstring
    """

    _max_record_id = 0
    _connection = None
    cache: "dict[int, TaskObject]" = {}

    def __init__(self, file_name=FILE):
        with open(file=file_name, encoding="utf-8") as file:
            params = json.load(file)

        try:
            self._connection = pymysql.connect(
                host=params["db_address"],
                port=params["db_port"],
                user=params["db_user"],
                password=params["db_password"],
                database=params["db_name"],
                cursorclass=pymysql.cursors.DictCursor
                if params["use_dict_cursor"]
                else None,
                autocommit=True,
            )
            log.info("Connected to database")
        except pymysql.Error as ex:
            log.error("Connection error: %s", ex)

    def _check_connection(self):
        if not self._connection:
            raise ConnectionError("Connection wasn`t established")

    def get_initial_state(self) -> str:
        """
        TODO docstring
        """
        self._check_connection()

        with self._connection.cursor() as cursor:
            cursor.execute(
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
            rows = cursor.fetchall()

            for row in rows:
                if row["record_id"] > self._max_record_id:
                    self._max_record_id = row["record_id"]
                entity = TaskObject(row["id"], row["record_id"], row["foo"], row["bar"])
                self.cache[row["id"]] = entity

        log.info("Max record id after initial state: %d", self._max_record_id)
        return json.dumps(self.cache, cls=TaskObjectEncoder)

    def get_update(self) -> str:
        """
        TODO docstring
        """
        self._check_connection()

        result_list = []

        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, record_id, foo, bar
                FROM test_table
                WHERE record_id > %s
                ORDER BY record_id;
                """,
                (self._max_record_id,),
            )
            rows = cursor.fetchall()
            for row in rows:
                if row["record_id"] > self._max_record_id:
                    self._max_record_id = row["record_id"]

                new_obj = TaskObject(
                    row["id"], row["record_id"], row["foo"], row["bar"]
                )
                if new_obj.entity_id not in self.cache:
                    self.cache[new_obj.entity_id] = new_obj
                    result_list.append(
                        PatchObject(
                            op="add",
                            path=f"/{new_obj.entity_id}",
                            value=json.dumps(new_obj, cls=TaskObjectEncoder),
                        )
                    )
                else:
                    old_obj = self.cache[new_obj.entity_id]
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
