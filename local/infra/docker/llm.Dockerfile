FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip curl && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

COPY services/llm/ services/llm/

ENV LLM_BACKEND=ollama
ENV LLM_MODEL=qwen2.5:72b
ENV LLM_API_URL=http://localhost:11434

EXPOSE 11434

CMD ["ollama", "serve"]
