import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model.model import Base

from errors import ParameterError


class Alchemy:
    def __init__(self, dburl=None, filename=None):
        if dburl:
            self._dburl = dburl
        elif filename:
            with open(filename, encoding="utf-8") as file:
                data = json.load(file)

                self._check_required_fields(data)

                dialect = data["dialect"]
                driver = data["driver"]
                username = data["username"]
                password = data["password"]
                host = data["host"]
                port = data["port"]
                database = data["database"]

                dburl = f"{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}"  # noqa: E501
        else:
            raise ParameterError(
                "No dburl or filename specified. Unable to initialize."
            )

        self._engine = create_engine(dburl)
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine)

    def get_session(self):
        """Возвращает сессию"""
        return self._session_factory()

    def _check_required_fields(self, data):
        required_fields = [
            "dialect",
            "driver",
            "username",
            "password",
            "host",
            "port",
            "database",
        ]
        missing_fields = [
            field
            for field in required_fields
            if field not in data or data[field] is None
        ]

        if missing_fields:
            raise ParameterError(
                f"Missing fields in configuration file: {', '.join(missing_fields)}"  # noqa: E501
            )
