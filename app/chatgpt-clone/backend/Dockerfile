# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing pyc files to disc (optional)
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to terminal (useful for logs)
ENV PYTHONUNBUFFERED 1

# Install system dependencies if needed (e.g., for certain libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt .
# Use --no-cache-dir to reduce layer size
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
# This assumes your FastAPI app structure is inside an 'app' directory
COPY ./app /app/app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for the API root path, defaulting to /api
# This is used by the CMD directive below.
ENV ROOT_PATH=/api

# Run the application using Uvicorn.
# Use 0.0.0.0 to allow connections from outside the container.
# Use the ROOT_PATH environment variable for the --root-path argument.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--root-path", "${ROOT_PATH}"]

# For development with hot-reloading (mount volume in docker-compose):
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--root-path", "${ROOT_PATH}"]