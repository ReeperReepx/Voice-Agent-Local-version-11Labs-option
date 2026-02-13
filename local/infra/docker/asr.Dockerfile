FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY services/asr/ services/asr/

ENV PYTHONPATH=/app
ENV ASR_DEVICE=cuda

CMD ["python3", "-c", "from services.asr.pingala.model_loader import load_model; load_model(); print('ASR model loaded')"]
