# Use an official Python runtime as a parent image
FROM python:3.9-alpine

ENV APP_VERSION="0.9.0"
# Install build dependencies (including gcc)
RUN apk add --no-cache build-base

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variable
ENV PYTHONUNBUFFERED=1
#Set Log Level (INFO, WARN, ERROR, FATAL)
ENV LOG_LEVEL=INFO

# Run the application
CMD ["python", "run.py"]

EXPOSE 1337