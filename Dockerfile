# Base Image
FROM python:3.8-slim

# Set environment variables to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC

# Update and install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port and specify the entry point
EXPOSE 5000
CMD ["python", "app.py"]
