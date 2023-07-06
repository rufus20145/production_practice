from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Alchemy:
    def __init__(self, dburl):
        self._dburl = dburl
        self._engine = create_engine(dburl)
        self._session_factory = sessionmaker(bind=self._engine)

    def session_factory(self):
        """Return a new Session"""
        Base.metadata.create_all(self._engine)
        return self._session_factory()
