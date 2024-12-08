# Use Python 3.8 image
FROM python:3.8

# Set working directory
WORKDIR /app

# Install system dependencies required by OpenCV
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

# Expose port for Flask app
EXPOSE 5000

# Start the application with Flask's development server (removes Gunicorn)
CMD ["python", "app.py"]
