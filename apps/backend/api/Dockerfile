# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /api

# Copy all files from the current directory to the /api directory in the container
COPY . /api

# Install system dependencies (if needed) and clean up afterward
RUN apt-get update && apt-get install -y gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Firestore service account key into the container
COPY slimeify-418ca51fd7e7.json /api/slimeify-418ca51fd7e7.json

ENV GOOGLE_APPLICATION_CREDENTIALS="/api/slimeify-418ca51fd7e7.json"

# Expose port 8080 (default for Flask/Gunicorn)
EXPOSE 8080

# Command to run the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
