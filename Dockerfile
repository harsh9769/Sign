# Use Python 3.8-slim image for a smaller base image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (using a virtual environment for isolation)
COPY requirements.txt ./ 
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Update PATH to include the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY . .

# Expose port for Flask app
EXPOSE 8000

# Start the application with Flask's development server
CMD ["python", "app.py"]
