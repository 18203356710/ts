
from redis import StrictRedis


class Config:
    DEBUG=None
    SECRET_KEY = 'vY6Y2QfSEFalEmuIaywYgu3O40PtdMuyhvWpLsfyDXaej7+T/Ry7Eg=='

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    SESSION_TYPE='redis'
    SESSION_REDIS= StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER= True
    PERMAENT_SESSION_LIFETIME= 86400
    SQLALCHEMY_DATABASE_URI= 'mysql://root:mysql@localhost/iHome'
    SQLALCHEMY_TRACK_MODIFICATIONS= False

class DevelopmentConfig(Config):
    DEBUG=True

class ProductionConfig(Config):
    DEBUG = False

config_dict={
    'development':DevelopmentConfig,
    'production':ProductionConfig
}