# Use NVIDIA's base image with GPU support and Python pre-installed
FROM nvidia/cuda:11.8.0-runtime-ubuntu20.04

# Install Python and required system dependencies for OpenCV and Redis
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip \
    python3-distutils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    redis-server && \
    apt-get clean

# Set the working directory
WORKDIR /app

# Copy application code to the container
COPY . /app

# Install Python dependencies
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Expose the application port and Redis port
EXPOSE 5000 6379

# Start Redis server and Flask app
CMD ["sh", "-c", "redis-server --daemonize yes && python3 app.py"]
