# Start with a Python base image
FROM python:3.10-slim

# Install required tools
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    wget \
    unzip \
    curl \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libxss1 libappindicator3-1 libasound2 libatk-bridge2.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Download and install Chrome (version matching your local one)
RUN wget https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.205/linux64/chrome-linux64.zip \
    && unzip chrome-linux64.zip \
    && mv chrome-linux64 /opt/chrome \
    && ln -s /opt/chrome/chrome /usr/bin/google-chrome

# Download and install matching ChromeDriver
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/131.0.6778.205/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app
WORKDIR /app

# Set environment variable so Selenium knows where Chrome is
ENV CHROME_BIN=/usr/bin/google-chrome

CMD ["gunicorn", "--timeout", "120", "-b", "0.0.0.0:5000", "app:app"]
