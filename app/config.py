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
    LOG_TYPE = os.environ.get("LOG_TYPE", "stream")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = "redis://redis:6379/"
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER') or '/tmp'
    IMAGES_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'gif'}
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True
    }
    APIFAIRY_UI = 'swagger_ui'
    
    # ldap integration
    LDAP_AUTH = False
    LDAP_HOST = '192.168.2.2'
    LDAP_BASE_DN = 'DC=adelante,DC=lan'
    LDAP_USER_DN = 'CN=Users'
    LDAP_GROUP_DN = 'CN=Groups'
    LDAP_USER_RDN_ATTR = 'CN'
    LDAP_USER_LOGIN_ATTR = 'samAccountname'
    LDAP_BIND_USER_DN = 'CN=Read Only,CN=Users,DC=adelante,DC=lan'
    LDAP_BIND_USER_PASSWORD = 'zp3N7qvu'
    # --
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # blueprints
    PHOTOSTORE_ENABLED = True
    DEFAULT_VOL_SIZE = int(os.getenv('DEFAULT_VOL_SIZE', 0)) or 107374182400
    DEFAULT_MEDIA_SIZE = int(os.getenv('DEFAULT_MEDIA_SIZE', 0)) or 4831838208
    # --
    broker_url = os.getenv('CELERY_BROKER_URL') or 'redis://localhost:6379'
    result_backend = os.getenv('CELERY_RESULT_BACKEND') or None

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/testdb.db'

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
