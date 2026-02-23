# Use a lightweight Python image as the base
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE backend.config.settings

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for psycopg2 and other packages
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev libxml2-dev libxslt1-dev pkg-config libcairo2-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy the rest of the application code (project root)
COPY . /app

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.config.wsgi:application"]
