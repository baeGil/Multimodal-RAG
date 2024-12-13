# Base image python
FROM python:3.11.7-slim

# working directory
WORKDIR /frontend

# Copy and run dependencies
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt --index-url=https://pypi.tuna.tsinghua.edu.cn/simple


# Copy Python files
COPY redis_client.py .
COPY streamlit_app.py .

# Run Streamlit app
CMD ["python", "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]