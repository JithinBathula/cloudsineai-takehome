import os
import logging
from flask import Flask, request, render_template
from config import config
from app.utils.helpers import format_timestamp  # moved here

def create_app(config_name):
    """Application factory function."""
    config_name = config_name or os.getenv('FLASK_CONFIG', 'default')
    app = Flask(__name__, instance_relative_config=False)

    # Load config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Logging
    logging.basicConfig(
        level=logging.INFO if not app.debug else logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    app.logger.info(f"App created with '{config_name}' config.")
    app.logger.info(f"Upload folder: {app.config.get('UPLOAD_FOLDER')}")

    if not app.config.get('VIRUSTOTAL_API_KEY'):
        app.logger.error("VIRUSTOTAL_API_KEY is not set! Check your .env file.")

    # Register custom Jinja2 filters
    app.jinja_env.filters['strftime'] = format_timestamp

    # Register Blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        app.logger.warning(f"404 Not Found: {request.path}")
        return render_template('404.html'), 404

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        app.logger.error(f"Unhandled Exception: {error}", exc_info=True)
        error_msg = str(error) if app.debug else None
        return render_template('500.html', error_message=error_msg), 500

    return app
