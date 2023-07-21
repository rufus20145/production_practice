import json
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from model.model import Base
from errors import ParameterError


class Alchemy:
    _instance: Optional["Alchemy"] = None

    def __new__(cls, *args, **kwargs) -> "Alchemy":
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self, dburl: Optional[str] = None, filename: Optional[str] = None
    ) -> None:
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

    def get_session(self) -> Session:
        """
        Get a new session.

        Returns:
            Session: The SQLAlchemy session object.
        """
        return self._session_factory()

    def _check_required_fields(self, fields: dict) -> None:
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
            if field not in fields or fields[field] is None
        ]

        if missing_fields:
            raise ParameterError(
                f"Missing fields in configuration file: {', '.join(missing_fields)}"  # noqa: E501
            )
