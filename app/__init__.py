# app/__init__.py
import os
import logging
from datetime import datetime # For custom filter
from flask import Flask, flash, redirect, url_for, request, render_template
from config import config

# --- Define the custom filter function ---
def format_timestamp(timestamp_int, fmt='%Y-%m-%d %H:%M:%S UTC'):
    """Converts a Unix timestamp integer to a formatted string."""
    if timestamp_int is None:
        return "N/A"
    try:
        dt_object = datetime.utcfromtimestamp(int(timestamp_int))
        return dt_object.strftime(fmt)
    except (ValueError, TypeError) as e:
        # In a real app, get the app logger here, but for simplicity:
        print(f"Error formatting timestamp {timestamp_int}: {e}")
        return "Invalid Date"


def create_app(config_name=None):
    """Application factory function."""
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app = Flask(__name__, instance_relative_config=False) # instance_relative_config often False if config.py is in root
    # Load configuration from config.py object
    app.config.from_object(config[config_name])
    print(f"--- Loading configuration: {config_name} ---")

    # Initialize configuration-specific parts (like creating UPLOAD_FOLDER)
    config[config_name].init_app(app)

    # Basic logging configuration
    logging.basicConfig(level=logging.INFO if not app.debug else logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    app.logger.info(f"Flask app '{app.name}' created with '{config_name}' config.") # Use app.name
    app.logger.info(f"Upload folder: {app.config.get('UPLOAD_FOLDER')}")
    if not app.config.get('VIRUSTOTAL_API_KEY'):
         app.logger.error("VIRUSTOTAL_API_KEY is not set! Check your .env file.")

    # --- Register Custom Template Filter ---
    app.jinja_env.filters['strftime'] = format_timestamp


    # --- Import and Register Blueprints ---
    # Import the blueprint object directly
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    # --- Global Error Handlers ---
    # Error handler 413 removed

    @app.errorhandler(404)
    def page_not_found(error):
         app.logger.warning(f"404 Not Found: {request.path}", exc_info=False)
         # Render the 404 template instead of redirecting
         return render_template('404.html'), 404

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        app.logger.error(f"Unhandled Exception: {error}", exc_info=True)
        # Render the 500 template instead of redirecting
        error_msg = str(error) if app.debug else None
        return render_template('500.html', error_message=error_msg), 500

    return app