# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

COPY apps/backend/setup.py .

RUN pip install -e . \
    && apt-get update && apt-get install -y gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project
COPY . .
# Copy the Firestore service account key into the container
COPY apps/backend/api/slimeify-418ca51fd7e7.json /app/slimeify-418ca51fd7e7.json

ENV GOOGLE_APPLICATION_CREDENTIALS="/app/slimeify-418ca51fd7e7.json"
# Add the app directory to Python path
ENV PYTHONPATH="/app"

# Expose port 8080 (default for Flask/Gunicorn)
EXPOSE 8080

# Command to run the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "apps.backend.api.main:app"]
