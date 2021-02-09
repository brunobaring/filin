import os

class BaseConfig(object):
    """Base configuration."""
    # DEBUG = False
    # BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('FILIN_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    UPLOAD_PATH = 'emotion/uploads'



class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    # BCRYPT_LOG_ROUNDS = 4
    DEBUG = True



class StagingConfig(BaseConfig):
    """Testing configuration."""
    # BCRYPT_LOG_ROUNDS = 4
    # PRESERVE_CONTEXT_ON_EXCEPTION = False
    DEBUG = True



class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
