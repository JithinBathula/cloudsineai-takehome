# Stage 1: Base Image
FROM python:3.9-slim as base

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies if any are needed (e.g., build tools for some packages)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Stage 2: Install Dependencies
FROM base as builder

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Application Image
FROM base as runtime

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app /app/app
COPY config.py .
COPY wsgi.py .
# We don't copy .env - it should be provided at runtime

# Create the upload directory (ensure path matches config.py if changed)
# Use a directory outside /app if preferred, but /app/uploads is simple
RUN mkdir -p /app/uploads && chown -R nobody:nogroup /app/uploads
VOLUME /app/uploads # Define mount point for uploads volume

# Create a non-root user and switch to it
RUN adduser --system --group --no-create-home appuser
USER appuser

# Expose the port the application runs on
EXPOSE 5000

# Set runtime environment variables
ENV FLASK_APP wsgi.py
ENV FLASK_CONFIG production # Default to production config

# Command to run the application using Gunicorn
# Point Gunicorn to the 'app' object within the 'wsgi.py' module (which is created by create_app)
# Use a sensible number of workers (adjust '4' based on instance CPU cores, e.g., 2 * num_cores + 1)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "330", "--log-level", "info", "wsgi:app"]