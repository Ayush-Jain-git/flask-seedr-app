# Start with a base image that includes Python
FROM python:3.10-slim

# Install necessary dependencies (e.g., wget, unzip, curl, jq for JSON parsing)
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Get the latest stable version of Chromium using the omahaproxy API
RUN CHROMIUM_VERSION=$(curl -s https://omahaproxy.appspot.com/all.json | jq -r '.[0].versions[0].current_version') \
    && echo "Chromium version: $CHROMIUM_VERSION" \
    && wget https://chromedriver.storage.googleapis.com/${CHROMIUM_VERSION}/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/ \
    && rm chromedriver_linux64.zip

# Install the necessary Python dependencies
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
