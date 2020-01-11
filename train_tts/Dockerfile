FROM pytorch/pytorch:1.3-cuda10.1-cudnn7-runtime

# Clone Mozilla TTS
RUN git clone https://github.com/mozilla/TTS.git && \
    cd TTS && \
    git checkout db7f3d3 && \
    pip install -r requirements.txt && \
    apt-get update && apt-get install -y wget espeak && \
    rm -rf /var/lib/apt/lists/*

# Add a custom attention layer
ADD attention.py TTS/layers/attention.py
