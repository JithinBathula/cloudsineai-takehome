# app/utils/helpers.py
import os
from flask import current_app
from werkzeug.utils import secure_filename

# allowed_file function removed

def get_safe_upload_path(filename):
     """Generates a safe path within the configured UPLOAD_FOLDER."""
     # Sanitize filename to prevent directory traversal or invalid names
     safe_filename = secure_filename(filename)
     if not safe_filename: # Handle cases where secure_filename returns empty (e.g., filename is just '.')
         safe_filename = "upload_" + str(os.urandom(8).hex()) # Generate a random name

     # Return the full path
     return os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)

def cleanup_file(filepath):
    """Safely removes a file if it exists, logging errors."""
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            current_app.logger.info(f"Cleaned up temporary file: {filepath}")
        except OSError as e:
            current_app.logger.error(f"Error removing temporary file {filepath}: {e}")
    elif filepath:
         current_app.logger.debug(f"Attempted to clean up non-existent file: {filepath}")