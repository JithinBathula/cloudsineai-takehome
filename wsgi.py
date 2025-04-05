import os
from app import create_app

# Create the Flask app instance using the factory
# Reads FLASK_CONFIG environment variable to determine configuration
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# This block is useful for running directly with `python wsgi.py` for local debugging,
# but Gunicorn should be used for production deployments.
if __name__ == "__main__":
    print(
        f"--- Starting Flask development server via wsgi.py (DEBUG={app.debug}) ---")
    # Use Flask's built-in server, listening on all interfaces if needed
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
