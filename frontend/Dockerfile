FROM python:3.11
WORKDIR /frontend

COPY requirements.txt .
COPY redis_client.py .
COPY streamlit_app.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]