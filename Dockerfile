# Use a base image with Python and dependencies
FROM python:3.10-slim

# Install necessary dependencies for Chromium and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg2 \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libgtk-3-0 \
    libnss3 \
    libgbm1 \
    chromium

# Install ChromeDriver manually
RUN CHROMIUM_VERSION=$(chromium --version | sed 's/.*Chromium \([0-9]*\)\..*/\1/') && \
    wget https://chromedriver.storage.googleapis.com/${CHROMIUM_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/bin/ && \
    rm chromedriver_linux64.zip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Set working directory
WORKDIR /app

# Expose the port
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
