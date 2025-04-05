import os
from app import create_app

# Create the Flask app instance using the factory
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# This block is for local dev only
if __name__ == "__main__":
    app.logger.debug(f"Starting development server (DEBUG={app.debug})")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
