from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import Config

from app.models.base import Base


class DB:
    """Hosts all functions for querying the database."""
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
        print("Creating all tables")
        Base.metadata.create_all(self.engine, checkfirst=True)
        self.Session = sessionmaker(bind=self.engine)
        Session = self.Session()
        Session.commit()

    def connect(self):
        return self.engine.connect()

    def execute(self, sqlstr, **kwargs):
        # https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.execute
        with self.engine.connect() as conn:
            return list(conn.execute(text(sqlstr), kwargs).fetchall())

    def make_session(self):
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
        Session = sessionmaker(engine, expire_on_commit=False)
        return Session()