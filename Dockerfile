# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app/
COPY . /app/

# Copy NGINX configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for NGINX
EXPOSE 80

# Run NGINX and uWSGI services
CMD service nginx start && uwsgi --ini uwsgi.ini
