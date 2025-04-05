import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a-very-insecure-default-key')
    DEBUG = False
    TESTING = False

    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY')
    VT_API_URL_FILES = "https://www.virustotal.com/api/v3/files"
    VT_API_URL_ANALYSES = "https://www.virustotal.com/api/v3/analyses/"
    VT_POLL_INTERVAL = 15
    VT_MAX_POLL_TIME = 300
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024

    @staticmethod
    def init_app(app):
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder and not os.path.exists(upload_folder):
            try:
                os.makedirs(upload_folder)
            except OSError as e:
                app.logger.error(f"Could not create upload folder: {e}")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    if os.getenv('FLASK_DEBUG') == '1':
        DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
