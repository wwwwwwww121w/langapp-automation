# Telegram Bot + Stable Diffusion (CPU mode на Railway, GPU на локальном ПК)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Установка PyTorch CPU (для Railway без GPU)
# Локально заменяется на CUDA версию
RUN pip install --no-cache-dir \
    torch==2.2.0 \
    torchvision==0.17.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Copy requirements
COPY requirements.txt .

# Установка остальных зависимостей (torch уже установлен выше)
RUN pip install --no-cache-dir \
    python-telegram-bot>=20.0 \
    python-dotenv>=1.0.0 \
    diffusers==0.27.2 \
    transformers==4.40.0 \
    accelerate==0.29.0 \
    safetensors>=0.4.2 \
    "huggingface_hub==0.23.0" \
    "Pillow>=10.0.0" \
    "ffmpeg-python>=0.2.0" \
    "requests>=2.31.0" \
    "aiohttp>=3.9.0" \
    "numpy<2"

# Copy project files
COPY . .

# Create output directories
RUN mkdir -p output/videos output/frames logs data models

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
# SD_MODEL можно переопределить в Railway переменных
ENV SD_MODEL=runwayml/stable-diffusion-v1-5
ENV SD_NUM_FRAMES=8
ENV SD_STEPS=25

# Run via entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
