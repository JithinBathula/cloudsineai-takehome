import os
import time
import requests
from flask import current_app


class VirusTotalError(Exception):
    pass


def _get_vt_config():
    api_key = current_app.config.get('VIRUSTOTAL_API_KEY')
    url_files = current_app.config.get('VT_API_URL_FILES')
    url_analyses = current_app.config.get('VT_API_URL_ANALYSES')

    if not all([api_key, url_files, url_analyses]):
        current_app.logger.critical("Missing VirusTotal API config.")
        raise VirusTotalError("Missing VirusTotal configuration.")

    return {
        "headers": {"x-apikey": api_key},
        "url_files": url_files,
        "url_analyses": url_analyses,
        "poll_interval": current_app.config.get('VT_POLL_INTERVAL', 15),
        "max_poll_time": current_app.config.get('VT_MAX_POLL_TIME', 300),
    }


def upload_to_virustotal(file_path):
    try:
        vt = _get_vt_config()
        filename = os.path.basename(file_path)
        current_app.logger.info(f"Uploading '{filename}' to VirusTotal")

        with open(file_path, 'rb') as f:
            response = requests.post(
                vt['url_files'],
                headers=vt['headers'],
                files={'file': (filename, f)},
                timeout=90
            )

        response.raise_for_status()
        analysis_id = response.json().get('data', {}).get('id')

        if analysis_id:
            return analysis_id, None
        return None, "VirusTotal returned an unexpected response format."

    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code == 401:
            return None, "Invalid VirusTotal API Key."
        if code == 429:
            return None, "VirusTotal API rate limit exceeded."
        return None, f"VirusTotal API error ({code})."

    except requests.exceptions.Timeout:
        return None, "Network timeout during upload."

    except Exception as e:
        current_app.logger.error(f"Error uploading to VirusTotal: {e}", exc_info=True)
        return None, f"Unexpected error: {e}"


def get_virustotal_report(analysis_id):
    try:
        vt = _get_vt_config()
        url = vt['url_analyses'] + analysis_id
        start_time = time.time()

        while time.time() - start_time < vt['max_poll_time']:
            try:
                response = requests.get(url, headers=vt['headers'], timeout=30)
                response.raise_for_status()
                data = response.json()
                status = data.get('data', {}).get('attributes', {}).get('status')

                if status == 'completed':
                    return data, None
                elif status in ['queued', 'inprogress']:
                    time.sleep(vt['poll_interval'])
                else:
                    return None, f"Unexpected scan status: '{status}'."

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    return None, "Scan report not found."
                elif e.response.status_code == 429:
                    time.sleep(vt['poll_interval'])
                else:
                    return None, f"API error ({e.response.status_code})"

            except Exception as e:
                current_app.logger.warning(f"Polling error: {e}")
                time.sleep(vt['poll_interval'])

        return None, "Timeout waiting for scan results."

    except Exception as e:
        current_app.logger.error(f"Error polling VirusTotal: {e}", exc_info=True)
        return None, f"Unexpected error while polling: {e}"
