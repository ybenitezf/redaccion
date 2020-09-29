from dotenv import load_dotenv
import os

# parse .env file if exists
load_dotenv()

class Config(object):
    ENV = 'development'
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY') or 'some-secret-of-my-own'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/auth_test.db'

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
