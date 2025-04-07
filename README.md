# CloudSineAI — VirusTotal File Scanner (Take-Home Assignment)

---

## 🧠 Overview

This project is a secure, containerized web application that allows users to upload files and scan them using the [VirusTotal API](https://developers.virustotal.com/). The app is built with Flask and Docker, and deployed on an AWS EC2 instance behind an Nginx reverse proxy.

---

## 🌐 Live Demo

You can try the deployed app here:

👉 [http://54.253.181.106/](http://54.253.181.106/)

This is hosted on an AWS EC2 instance, running the containerized Flask app behind Nginx and Gunicorn.

## 🚀 Features

- ✅ File upload with basic validation (via Flask)
- ✅ VirusTotal integration for file scanning
- ✅ Dynamic, user-friendly result display
- ✅ Toggle-able full JSON scan report
- ✅ Flash messages for user feedback
- ✅ Spinner/loading indicator during scans
- ✅ Dockerized for easy deployment
- ✅ Runs in production behind Nginx + Gunicorn

---

## ⚙️ Tech Stack

- Python 3.9
- Flask (App Factory Pattern)
- Gunicorn (WSGI Server)
- Nginx (Reverse Proxy)
- Docker + Docker Compose
- Bootstrap 5 (UI Framework)
- JavaScript (custom form handling)
- AWS EC2 (Ubuntu 20.04)

---

## 📂 Project Structure

- `app/` – Main application code
  - `main/` – Blueprint routes and views
  - `services/` – VirusTotal API logic
  - `utils/` – Helper functions (file handling, date formatting)
  - `templates/` – Jinja2 HTML templates
  - `static/` – CSS and JS
- `uploads/` – Temp storage for uploaded files
- `config.py` – Environment-based app configs
- `wsgi.py` – Entry point for Gunicorn
- `nginx/` – Custom Nginx config
- `Dockerfile` – Multi-stage build
- `docker-compose.yml` – Orchestrates Flask + Nginx containers

---

## 🔐 Security Considerations

- File names are sanitized using `secure_filename`
- Uploaded files are deleted after scanning
- All API keys and secrets are managed through `.env`
- Error handling is implemented for both file and network errors
- Scan result polling includes timeout handling to prevent infinite loops

---

## 🛠 How to Run the Project

1. Clone the repository onto an EC2 instance.
2. Ensure Docker and Docker Compose are installed.
3. Add a `.env` file at the root with your VirusTotal API key and secret key:
   - `VIRUSTOTAL_API_KEY=your_api_key_here`
   - `SECRET_KEY=your_flask_secret`
4. Build and run the containers:
   - `docker-compose up --build`
5. Open a browser and go to:
   - `http://<your-ec2-ip>` or `http://<your-ec2-ip>:8080` (depending on port used)

---

## 📈 Example Workflow

1. User uploads a file.
2. App sends the file to VirusTotal.
3. App polls VirusTotal for the scan report.
4. Results are shown on the page — color-coded and detailed.

---

## 🌟 Enhancements Added

- Dockerized deployment with multi-stage builds
- Flash messaging and Bootstrap form validation
- Collapsible full scan result (JSON)
- Logging with custom timestamps
- Spinner UI while scanning
- Modular service structure for VirusTotal logic
- Static file serving via Nginx

---

## 📌 Notes

- This version does not use a database; data is ephemeral.
- No login/auth required — this is a single-user public demo.
- The app works best with small files under the VirusTotal upload limit (32MB for free API).
