import os
from flask import (render_template, request, redirect, url_for, flash, current_app, jsonify)
from . import main
from ..utils.helpers import get_safe_upload_path, cleanup_file
from ..services.virustotal import upload_to_virustotal, get_virustotal_report


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file_to_scan' not in request.files or not request.files['file_to_scan'].filename:
            flash('Please select a file to upload.', 'warning')
            return redirect(request.url)

        file = request.files['file_to_scan']
        filepath = None
        original_filename = file.filename 

        try:
            filepath = get_safe_upload_path(original_filename)
            file.save(filepath)
            current_app.logger.info(
                f"File '{original_filename}' saved temporarily to: {filepath}")

            analysis_id, error = upload_to_virustotal(filepath)

            if error or not analysis_id:
                error_message = error or "Failed to initiate scan with VirusTotal (no analysis ID returned)."
                flash(f'VirusTotal Upload Error: {error_message}', 'danger')
                cleanup_file(filepath)
                return redirect(request.url)

            current_app.logger.info(
                f"Polling for results for Analysis ID: {analysis_id}")
            scan_results, error = get_virustotal_report(analysis_id)

            cleanup_file(filepath)

            if error:
                flash(f'VirusTotal Scan Error: {error}', 'danger')
                return render_template('index.html', filename=original_filename, results=None)
            elif scan_results:
                flash('Scan completed!', 'success')
                return render_template('index.html', results=scan_results, filename=original_filename)
            else:
                flash('Unknown issue retrieving scan results after polling.', 'warning')
                return render_template('index.html', filename=original_filename, results=None)

        except Exception as e:
            current_app.logger.error(
                f"Error processing upload for '{original_filename}': {e}", exc_info=True)
            flash(
                f'An internal server error occurred while processing the file.', 'danger')
            cleanup_file(filepath)
            return redirect(url_for('.index'))

    return render_template('index.html', results=None, filename=None)