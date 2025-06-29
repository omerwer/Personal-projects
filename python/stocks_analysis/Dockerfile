FROM python:3.10-slim

# Install system dependencies including Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    fonts-dejavu-core \
    fonts-liberation \
    curl \
    && apt-get clean

# Install wkhtmltoimage
RUN curl -LO https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb && \
    apt install -y ./wkhtmltox_0.12.6-1.bionic_amd64.deb && \
    ln -s /usr/local/bin/wkhtmltoimage /usr/bin/wkhtmltoimage

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY ta_installs.txt .
RUN pip install --no-cache-dir -r ta_installs.txt

# Copy source code
COPY . .

# Start FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
