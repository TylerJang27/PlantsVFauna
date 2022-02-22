import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@172.20.0.10/{}'\
        .format(os.environ.get('POSTGRES_USER'),
                os.environ.get('POSTGRES_PASSWORD'),
                os.environ.get('POSTGRES_DB'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False