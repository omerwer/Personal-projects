FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    fonts-dejavu-core \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY ta_installs.txt .
RUN pip install --no-cache-dir -r ta_installs.txt

# Copy app code
COPY . .

# Start your FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
