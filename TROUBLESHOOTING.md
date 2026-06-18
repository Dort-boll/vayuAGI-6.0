# 🛠️ VAYU AGI 6 Troubleshooting Guide

### 1. GUI opens, but VAYU says "[offline] Processed securely"
**Cause**: The system cannot reach Ollama.
**Fix**: 
- Ensure Ollama is installed and running (`ollama serve`).
- Pull models: `ollama pull deepseek-r1:14b qwen2.5:7b`.

### 2. 1.1.1.1 DNS / Web Search Fails
**Cause**: Cloudflare DoH endpoint is blocked by your firewall.
**Fix**: Open `vayu_agi/config.py` and change `doh_enabled = False`.

### 3. Text-to-Speech (TTS) doesn't make sound
**Cause**: `pyttsx3` requires audio drivers. Headless cloud servers lack audio output.
**Fix**: Install ALSA: `sudo apt-get install alsa-utils espeak` (Linux).

### 4. Application crashes with "RateLimitError"
**Cause**: Sent more than 30 requests in 60 seconds.
**Fix**: Wait 60 seconds or edit `vayu_agi/config.py` to increase `rate_limit_per_min`.
