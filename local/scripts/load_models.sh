#!/bin/bash
# Download all model weights for VisaWire Local Voice Agent
set -e

echo "=== VisaWire Local: Model Loader ==="

# 1. LLM — Qwen2.5-72B-Instruct via Ollama
echo ""
echo "--- Loading Qwen2.5-72B-Instruct via Ollama ---"
if command -v ollama &> /dev/null; then
    ollama pull qwen2.5:72b
    echo "Qwen2.5-72B loaded."
else
    echo "WARNING: Ollama not installed. Install from https://ollama.com"
    echo "Then run: ollama pull qwen2.5:72b"
fi

# 2. ASR — Pingala V1 Universal (shunyalabs)
echo ""
echo "--- Loading Pingala V1 Universal ASR model ---"
python3 -c "
from pingala_shunya import PingalaTranscriber
print('Downloading Pingala V1 Universal...')
t = PingalaTranscriber(model_name='shunyalabs/pingala-v1-universal', backend='transformers')
print('Pingala V1 Universal downloaded.')
" 2>&1 || echo "WARNING: Failed to download Pingala V1. Run: pip install pingala-shunya"

# 3. TTS — Qwen3-TTS VoiceDesign (English)
echo ""
echo "--- Loading Qwen3-TTS VoiceDesign (English) ---"
python3 -c "
import torch
from qwen_tts import Qwen3TTSModel
print('Downloading Qwen3-TTS VoiceDesign...')
Qwen3TTSModel.from_pretrained('Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign', device_map='cpu', dtype=torch.float32)
print('Qwen3-TTS VoiceDesign downloaded.')
" 2>&1 || echo "WARNING: Failed to download Qwen3-TTS. Run: pip install qwen-tts"

# 4. TTS — Parler-TTS (Hindi)
echo ""
echo "--- Loading Parler-TTS Mini v1 (Hindi) ---"
python3 -c "
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
print('Downloading Parler-TTS Mini v1...')
AutoTokenizer.from_pretrained('parler-tts/parler-tts-mini-v1')
ParlerTTSForConditionalGeneration.from_pretrained('parler-tts/parler-tts-mini-v1')
print('Parler-TTS Mini v1 downloaded.')
" 2>&1 || echo "WARNING: Failed to download Parler-TTS. Run: pip install git+https://github.com/huggingface/parler-tts.git"

echo ""
echo "=== Model loading complete ==="
