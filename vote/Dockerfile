# Define a base stage that uses the official python runtime base image
FROM python:3.11-slim

# Add curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Set the application directory
WORKDIR /usr/local/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install watchdog
ENV FLASK_ENV=development
# CMD ["python", "app.py"]

EXPOSE 80

# Define our command to be run when launching the container
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80", "--log-file", "-", "--access-logfile", "-", "--workers", "4", "--keep-alive", "0"]
