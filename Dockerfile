FROM runpod/worker-comfyui:5.5.1-base

# Установка git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Клонирование кастомных нод
WORKDIR /comfyui/custom_nodes
RUN git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git
RUN git clone https://github.com/fannovel16/ComfyUI-Frame-Interpolation.git
RUN git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git
RUN git clone https://github.com/yolain/ComfyUI-Easy-Use.git
RUN git clone https://github.com/kijai/ComfyUI-KJNodes.git

# Установка Python-пакетов
RUN pip install --no-cache-dir opencv-python accelerate gguf runpod requests

# Скачивание моделей (опционально, если не используешь Network Volume)

# Копирование handler и workflow
COPY handler.py /handler.py
COPY Wan22-I2V-Remix-100.json /comfyui/workflow.json

# Запуск handler
CMD ["python", "-u", "/handler.py"]
