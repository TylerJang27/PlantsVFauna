from sqlalchemy import Column, Integer, String, Sequence, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from app.models.base import Base
from app.config import Config
import random
import string

import datetime

class User(Base):
    __tablename__ = 'users'
    users_id_seq = Sequence('users_id_seq', start=10)
    uid = Column(Integer, users_id_seq, server_default=users_id_seq.next_value(), primary_key=True)
    username = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String, nullable=False)


    def __repr__(self):
        return "<User(uid='%d', username='%s', email='%s')>" % (
                             self.uid, self.username, self.email)

    def __init__(self, uid, email, username, password=None):
        self.uid = uid
        self.email = email
        self.username = username
        if password is not None:
            self.password = generate_password_hash(password)

