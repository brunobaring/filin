import os

class BaseConfig(object):
    """Base configuration."""
    # DEBUG = False
    # BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('FILIN_SECRET_KEY')
    UPLOAD_PATH = 'emotion/uploads'

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    # BCRYPT_LOG_ROUNDS = 4
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('FILIN_DATABASE_URL') + 'dev'

class StagingConfig(BaseConfig):
    """Testing configuration."""
    # BCRYPT_LOG_ROUNDS = 4
    # PRESERVE_CONTEXT_ON_EXCEPTION = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('FILIN_DATABASE_URL') + 'stage'

class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('FILIN_DATABASE_URL') + 'prod'