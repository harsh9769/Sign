FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port for the Flask app
EXPOSE 5000

# Start the application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--worker-class", "eventlet", "--workers", "1"]
