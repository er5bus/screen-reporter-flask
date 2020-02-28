import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "hard to guess string")
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    FLASK_MAIL_SENDER = os.getenv('FLASK_MAIL_SENDER')

    TRELLO_APP_KEY = "22ac062e43a16df65c5325dd965f3d1a"
    JWT_ACCESS_TOKEN_EXPIRES = False
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hard to guess string")
    JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY", "hard to guess string")
    JWT_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY", "hard to guess string")
    JWT_ERROR_MESSAGE_KEY = 'message'

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'sqlite:///' + os.path.join(Config.PROJECT_DIR, 'data', 'data-dev.sqlite'))
    DEBUG= True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///' +  os.path.join(Config.PROJECT_DIR, 'data', 'data-test.sqlite'))


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' +  os.path.join(Config.PROJECT_DIR, 'data', 'data.sqlite'))

    @classmethod
    def init_app(cls, app):
        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
