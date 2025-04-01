# Start with a base image that includes Python
FROM python:3.10-slim

# Install necessary dependencies (e.g., wget, unzip, etc.)
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium and ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium=90.0.4430.93-1 \
    chromium-chromedriver=90.0.4430.93-1

# Install any other dependencies you need
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable to use Chromium as the browser for Selenium
ENV CHROMIUM_BINARY=/usr/bin/chromium

# Copy your application code into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Expose the port your app will run on (optional, adjust if needed)
EXPOSE 5000

# Command to run your application (adjust for your app)
CMD ["python", "app.py"]
