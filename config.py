import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path) # Load .env file if it exists

# Check for essential keys after attempting load
if not os.environ.get('VIRUSTOTAL_API_KEY'):
     print("WARNING: VIRUSTOTAL_API_KEY not found in environment or .env file.")
if not os.environ.get('SECRET_KEY'):
     print("WARNING: SECRET_KEY not found in environment or .env file.")


class Config:
    """Base configuration settings."""
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-default-fallback-secret-key-is-insecure'
    DEBUG = False
    TESTING = False

    # File Upload Settings
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    # ALLOWED_EXTENSIONS removed
    # MAX_CONTENT_LENGTH removed

    # VirusTotal API Settings
    VIRUSTOTAL_API_KEY = os.environ.get('VIRUSTOTAL_API_KEY')
    VT_API_URL_FILES = "https://www.virustotal.com/api/v3/files"
    VT_API_URL_ANALYSES = "https://www.virustotal.com/api/v3/analyses/"
    VT_POLL_INTERVAL = 15  # Seconds between checking scan status
    VT_MAX_POLL_TIME = 300 # Maximum seconds to wait for results (5 minutes)

    @staticmethod
    def init_app(app):
        """Initialize application-specific settings."""
        # Ensure the upload folder exists
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder and not os.path.exists(upload_folder):
            try:
                os.makedirs(upload_folder)
                print(f"Created upload folder: {upload_folder}")
            except OSError as e:
                print(f"ERROR: Could not create upload folder: {upload_folder}. Error: {e}")


class DevelopmentConfig(Config):
    """Development configuration settings."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration settings."""
    # DEBUG is False by default in Config
    if os.environ.get('FLASK_DEBUG') == '1':
         print("Warning: FLASK_DEBUG=1 detected in ProductionConfig. Forcing DEBUG=False.")
         DEBUG = False


class TestingConfig(Config):
    """Testing configuration settings."""
    TESTING = True
    DEBUG = True


# Dictionary mapping config names to their classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}