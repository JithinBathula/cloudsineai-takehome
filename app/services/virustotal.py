import requests
import time
import os
from flask import current_app 

class VirusTotalError(Exception):
    """Custom exception for VirusTotal service errors."""
    pass


def _get_vt_config():
    """Helper to fetch and validate required VirusTotal config."""
    api_key = current_app.config.get('VIRUSTOTAL_API_KEY')
    url_files = current_app.config.get('VT_API_URL_FILES')
    url_analyses = current_app.config.get('VT_API_URL_ANALYSES')
    poll_interval = current_app.config.get('VT_POLL_INTERVAL', 15)
    max_poll_time = current_app.config.get('VT_MAX_POLL_TIME', 300)

    if not all([api_key, url_files, url_analyses]):
        current_app.logger.critical("VirusTotal API Key or URL(s) are not configured.")
        raise VirusTotalError("Server configuration error: VirusTotal settings missing.")

    return {
        "api_key": api_key,
        "url_files": url_files,
        "url_analyses": url_analyses,
        "poll_interval": poll_interval,
        "max_poll_time": max_poll_time,
        "headers": {'x-apikey': api_key}
    }


def upload_to_virustotal(file_path):
    try:
        vt_config = _get_vt_config()
    except VirusTotalError as e:
        return None, str(e)

    filename = os.path.basename(file_path)
    current_app.logger.info(f"Uploading '{filename}' to VirusTotal...")

    try:
        with open(file_path, 'rb') as f:
            files_payload = {'file': (filename, f)}
            response = requests.post(
                vt_config['url_files'],
                headers=vt_config['headers'],
                files=files_payload,
                timeout=90
            )
            response.raise_for_status()

        current_app.logger.debug(f"VT Upload Response Status: {response.status_code} for '{filename}'")

        result = response.json()
        analysis_id = result.get('data', {}).get('id')

        if analysis_id:
            current_app.logger.info(f"VirusTotal upload successful. Analysis ID: {analysis_id}")
            return analysis_id, None
        else:
            current_app.logger.error(f"Unexpected response format from VT upload for '{filename}': {result}")
            return None, "VirusTotal returned an unexpected response format after upload."

    except requests.exceptions.Timeout:
        current_app.logger.error(f"Timeout during VirusTotal upload for '{filename}'.")
        return None, "Network timeout during file upload to VirusTotal."
    
    except requests.exceptions.HTTPError as e:
        current_app.logger.error(f"HTTP Error during VT upload for '{filename}': {e.response.status_code} {e.response.text}")

        if e.response.status_code == 401:
            return None, "VirusTotal API Key is invalid or missing permissions."
        elif e.response.status_code == 429:
            return None, "VirusTotal API rate limit exceeded. Please try again later."
        return None, f"VirusTotal API error ({e.response.status_code}). Please check server logs."
    
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Network error during VT upload for '{filename}': {e}", exc_info=True)
        return None, f"Network error communicating with VirusTotal: {e}"
    except Exception as e:
        current_app.logger.error(f"Unexpected error during VT upload for '{filename}': {e}", exc_info=True)
        return None, f"An unexpected server error occurred during upload: {e}"


def get_virustotal_report(analysis_id):
    try:
        vt_config = _get_vt_config()
    except VirusTotalError as e:
        return None, str(e)

    url = vt_config['url_analyses'] + analysis_id
    start_time = time.time()
    poll_interval = vt_config['poll_interval']
    max_poll_time = vt_config['max_poll_time']

    current_app.logger.info(f"Polling for VirusTotal report: {analysis_id} (Interval: {poll_interval}s, Timeout: {max_poll_time}s)")

    while time.time() - start_time < max_poll_time:
        try:
            response = requests.get(
                url, headers=vt_config['headers'], timeout=30)
            response.raise_for_status()

            result = response.json()
            status = result.get('data', {}).get('attributes', {}).get('status')

            if status == 'completed':
                current_app.logger.info(
                    f"VirusTotal scan completed for {analysis_id}.")
                return result, None
            elif status in ['queued', 'inprogress']:
                current_app.logger.debug(
                    f"Scan status ({analysis_id}): {status}. Waiting {poll_interval}s...")
                time.sleep(poll_interval)
            else:
                current_app.logger.warning(f"VirusTotal scan ({analysis_id}) has unexpected status: {status}. Response: {result}")
                return None, f"Scan failed or encountered an unexpected status: '{status}'."

        except requests.exceptions.Timeout:
            current_app.logger.warning(f"Timeout waiting for VirusTotal report chunk ({analysis_id}). Retrying...")
            time.sleep(poll_interval)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                current_app.logger.error(f"Analysis ID {analysis_id} not found on VirusTotal.")
                return None, f"Scan report not found (ID: {analysis_id}). It might be invalid or expired."
            
            elif e.response.status_code == 429:
                current_app.logger.warning(f"Rate limit hit while polling for {analysis_id}. Retrying after {poll_interval}s.")
                time.sleep(poll_interval)

            else:
                current_app.logger.error(
                    f"HTTP Error fetching VT report ({analysis_id}): {e.response.status_code} {e.response.text}")
                # For persistent HTTP errors during polling, maybe stop trying?
                return None, f"VirusTotal API error ({e.response.status_code}) while retrieving report."
        except requests.exceptions.RequestException as e:
            current_app.logger.error(
                f"Network error fetching VT report ({analysis_id}): {e}", exc_info=False)
            # Continue polling for transient network errors, maybe with increasing backoff?
            current_app.logger.info(
                f"Network error, waiting {poll_interval}s before retrying report fetch for {analysis_id}.")
            time.sleep(poll_interval)
        except Exception as e:
            current_app.logger.error(
                f"Unexpected error fetching VT report ({analysis_id}): {e}", exc_info=True)
            return None, f"An unexpected server error occurred while fetching the report: {e}"

    current_app.logger.warning(
        f"Timeout exceeded polling for VirusTotal report ({analysis_id}) after {max_poll_time}s.")
    return None, "Timeout: Scan results were not available within the allowed time."
