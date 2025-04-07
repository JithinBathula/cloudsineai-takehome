from flask import render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from ..utils.results_helper import analyze_scan_results
from . import main
from ..utils.helpers import is_allowed_file, get_safe_upload_path, cleanup_file
from ..services.virustotal import upload_to_virustotal, get_virustotal_report


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file_to_scan')

        if not file or not file.filename:
            flash('Please select a file to upload.', 'warning')
            return redirect(request.url)

        original_filename = secure_filename(file.filename)
        if not is_allowed_file(original_filename):
            flash('File type not allowed. Please upload a valid file type.', 'danger')
            return redirect(request.url)

        filepath = None
        try:
            filepath = get_safe_upload_path(original_filename)
            file.save(filepath)
            current_app.logger.info(f"File '{original_filename}' saved to: {filepath}")

            analysis_id, error = upload_to_virustotal(filepath)
            if error or not analysis_id:
                flash(f'VirusTotal Upload Error: {error or "Unknown error."}', 'danger')
                return redirect(request.url)

            cleanup_file(filepath)

            scan_results, error = get_virustotal_report(analysis_id)
            if error:
                flash(f'VirusTotal Scan Error: {error}', 'danger')
                session['scan_context'] = analyze_scan_results(None, original_filename)
            else:
                flash('Scan completed!', 'success')
                session['scan_context'] = analyze_scan_results(scan_results, original_filename)

            return redirect(url_for('.index'))  # ⬅️ Redirect to GET
        except Exception as e:
            current_app.logger.error(f"Error processing upload: {e}", exc_info=True)
            flash('An internal error occurred while processing the file.', 'danger')
            if filepath:
                cleanup_file(filepath)
            return redirect(url_for('.index'))

    # GET request: show result if available
    context = session.pop('scan_context', None)
    if context:
        return render_template('index.html', **context)

    return render_template('index.html', results=None, filename=None)
