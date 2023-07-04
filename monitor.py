"""
TODO module docstring 
"""
import json
import logging as log

import pymysql

FILE = "connection_params.json"


class ChangeMonitor:
    """
    TODO class docstring
    """

    _max_record_id = 0
    _connection = None

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
            )
            log.info("Connected to database")
        except pymysql.Error as ex:
            log.error("Connection error: %s", ex)

    def _check_connection(self):
        if not self._connection:
            raise NotInitializedError("Connection wasn't initialized")

    def get_initial_state(self):
        """
        TODO docstring
        """
        self._check_connection()

        result = {}
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
                entity_id = row["id"]
                foo = row["foo"]
                bar = row["bar"]
                row_data = {"foo": foo, "bar": bar}
                result[entity_id] = row_data

        json_data = json.dumps(result, indent=4)
        print(json_data)
        print(f"Max record id after initial state: {self._max_record_id}")

    def get_patch(self):
        """
        TODO docstring
        """
        self._check_connection()

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
                print(f"{row['id']}\t{row['record_id']}\t\t{row['foo']}\t{row['bar']}")
                if row["record_id"] > self._max_record_id:
                    self._max_record_id = row["record_id"]

        print(f"Now max record id after patch: {self._max_record_id}")
