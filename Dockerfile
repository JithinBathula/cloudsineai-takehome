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

# Create a non-root user and group FIRST
RUN addgroup --system appgroup && adduser --system --ingroup appgroup --no-create-home appuser

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
# Important: Copy code BEFORE changing ownership of /app if needed, or copy to a temp location first
COPY app /app/app
COPY config.py .
COPY wsgi.py .

# Create the upload directory
RUN mkdir -p /app/uploads

# --- Change ownership of the uploads directory to the appuser ---
# Use chown BEFORE switching user
RUN chown -R appuser:appgroup /app/uploads
# Optional: If appuser needed write access to other parts of /app (unlikely here)
# RUN chown -R appuser:appgroup /app

# Define mount point for uploads volume
VOLUME /app/uploads

# Switch to the non-root user
USER appuser

# Expose the port the application runs on
EXPOSE 5000

# Set runtime environment variables
ENV FLASK_APP wsgi.py
ENV FLASK_CONFIG production

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "330", "--log-level", "info", "wsgi:app"]