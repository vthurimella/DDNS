# Use the official Python slim image from Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python script into the container
COPY cloudflare.py /app/

# Install any dependencies if required
RUN pip install aiohttp

# Define the entry point for the container
ENTRYPOINT ["python", "cloudflare.py"]
