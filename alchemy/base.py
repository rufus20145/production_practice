import json

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Alchemy:
    def __init__(self, dburl=None, filename=None):
        if dburl:
            self._dburl = dburl
        elif filename:
            with open(filename, encoding="utf-8") as file:
                data = json.load(file)

                dialect = data["dialect"]
                driver = data["driver"]
                username = data["username"]
                password = data["password"]
                host = data["host"]
                port = data["port"]
                database = data["database"]

                dburl = f"{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}"

        self._engine = create_engine(dburl)
        self._session_factory = sessionmaker(bind=self._engine)

    def session_factory(self):
        """Return a new Session"""
        Base.metadata.create_all(self._engine)
        return self._session_factory()
