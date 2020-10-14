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

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/auth_test.db'

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
