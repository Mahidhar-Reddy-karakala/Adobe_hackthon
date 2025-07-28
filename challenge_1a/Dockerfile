# # Dockerfile
# # Use an official Python runtime as a parent image, slim for size
# FROM --platform=linux/amd64 python:3.9-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the requirements file into the container at /app
# COPY requirements.txt /app/

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application code
# COPY . /app

# # Make sure the input and output directories exist (they will be mounted anyway)
# # RUN mkdir -p /app/input /app/output

# # Run main.py when the container launches
# # The command aligns with the expected execution: process all PDFs in /app/input
# CMD ["python", "main.py"]


# Dockerfile
# Dockerfile
# Dockerfile
# Use an official Python runtime as a parent image, slim for size
# Note: The warning about --platform flag is just a warning, the build should work.
# Dockerfile
FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# No model caching step needed

CMD ["python", "main.py"]