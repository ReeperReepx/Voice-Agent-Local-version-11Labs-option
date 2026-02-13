FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/ services/
COPY web/ web/

ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "services.api.http_gateway:app", "--host", "0.0.0.0", "--port", "8000"]
