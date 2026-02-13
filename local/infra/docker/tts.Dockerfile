FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip espeak-ng && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY services/tts/ services/tts/

ENV PYTHONPATH=/app
ENV TTS_DEVICE=cuda

CMD ["python3", "-c", "print('TTS service ready')"]
