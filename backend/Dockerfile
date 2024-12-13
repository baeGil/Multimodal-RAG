# Use python base image
FROM python:3.11.7-slim

# working directory
WORKDIR /backend

# copy dependencies file
COPY requirements.txt .

# Upgrade pip, install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --index-url=https://pypi.tuna.tsinghua.edu.cn/simple

# Install libGL
RUN apt-get update && apt-get install -y \
    libgl1 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy folder
COPY ./app ./app
COPY ./data ./data

# Run fast api 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

