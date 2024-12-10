# backend/Dockerfile
FROM python:3.12

# # Cài đặt thư mục làm việc
WORKDIR /backend

# # Copy dependencies
COPY requirements.txt .

# # Copy folder
COPY ./app ./app
COPY ./data ./data

# # Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt libGL và các gói phụ thuộc cần thiết
RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# # Chạy FastAPI với Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
