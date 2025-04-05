import os
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'exe', 'pdf', 'zip', 'docx', 'xlsx', 'txt', 'jpg', 'png', 'js', 'txt'}

def is_allowed_file(filename):
    """
    Check if the file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_safe_upload_path(filename):
    """
    Generate a safe, unique path within the configured UPLOAD_FOLDER.
    Sanitizes filename to avoid injection or traversal vulnerabilities.
    """
    safe_filename = secure_filename(filename)
    if not safe_filename:
        # If filename is invalid (e.g. just '.'), generate a random fallback
        safe_filename = "upload_" + os.urandom(8).hex()
    return os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)

def cleanup_file(filepath):
    """
    Safely removes a file if it exists, and logs the outcome.
    """
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            current_app.logger.info(f"Cleaned up temporary file: {filepath}")
        except OSError as e:
            current_app.logger.error(f"Error removing temporary file {filepath}: {e}")
    elif filepath:
        current_app.logger.debug(f"Attempted to clean up non-existent file: {filepath}")

def format_timestamp(timestamp_int, fmt='%Y-%m-%d %H:%M:%S UTC'):
    """
    Converts a Unix timestamp to a human-readable string.
    Used in Jinja templates with the `strftime` filter.
    """
    if timestamp_int is None:
        return "N/A"
    try:
        dt_object = datetime.utcfromtimestamp(int(timestamp_int))
        return dt_object.strftime(fmt)
    except (ValueError, TypeError) as e:
        current_app.logger.error(f"Error formatting timestamp {timestamp_int}: {e}")
        return "Invalid Date"
