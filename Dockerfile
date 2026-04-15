FROM runpod/worker-comfyui:5.5.1-base

# Даем сети время для стабильной работы
RUN sleep 20

# Установка git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Клонируем все кастомные ноды (как в твоём поде)
WORKDIR /comfyui/custom_nodes
RUN git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git
RUN git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git
RUN git clone https://github.com/yolain/ComfyUI-Easy-Use.git
RUN git clone https://github.com/fannovel16/ComfyUI-Frame-Interpolation.git
RUN git clone https://github.com/kijai/ComfyUI-KJNodes.git

# Устанавливаем зависимости
RUN pip install --no-cache-dir opencv-python accelerate gguf runpod requests

# Копируем handler и workflow
COPY handler.py /handler.py
COPY Wan22-I2V-Remix-100-API.json /comfyui/workflow.json

# Копируем конфиг extra_model_paths.yaml
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml

# Запускаем handler
CMD ["python", "-u", "/handler.py"]
