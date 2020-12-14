from dotenv import load_dotenv
import os

# parse .env file if exists
load_dotenv()


class Config(object):
    ENV = 'development'
    DEBUG = True
    SECRET_KEY = 'some-secret-of-my-own'


class TestConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
