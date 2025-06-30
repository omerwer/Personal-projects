# Use official Ubuntu base
FROM ubuntu:22.04

# Set environment vars
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Install Python and required system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    wget \
    build-essential \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    fonts-dejavu-core \
    fonts-liberation \
    wkhtmltopdf \
    && apt-get clean

# Ensure python and pip are available as 'python' and 'pip'
RUN ln -s /usr/bin/python3.10 /usr/bin/python && ln -s /usr/bin/pip3 /usr/bin/pip

# Install wkhtmltoimage manually (same as before)
RUN curl -LO https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb && \
    apt install -y ./wkhtmltox_0.12.6-1.bionic_amd64.deb && \
    ln -sf /usr/local/bin/wkhtmltoimage /usr/bin/wkhtmltoimage

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY ta_installs.txt .
RUN pip install --no-cache-dir -r ta_installs.txt

# Copy app code
COPY . .

# Debugging: show tesseract location and version
RUN which tesseract && tesseract --version

# Expose port and run FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
