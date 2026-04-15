# Используем официальный образ ComfyUI от RunPod
FROM runpod/workers:comfyui-base-1.4.0

# Даем сети время для стабильной работы
RUN sleep 20

# Клонируем недостающие кастомные ноды
WORKDIR /comfyui/custom_nodes
RUN git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git
RUN git clone https://github.com/fannovel16/ComfyUI-Frame-Interpolation.git
RUN git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git
RUN git clone https://github.com/yolain/ComfyUI-Easy-Use.git

# Устанавливаем Python-пакеты (соответствуют твоему поду)
RUN pip install --no-cache-dir opencv-python==4.13.0.92 \
    sentencepiece==0.2.1 \
    accelerate \
    gguf \
    runpod \
    requests

# Копируем твой handler и workflow
COPY handler.py /handler.py
COPY Wan22-I2V-Remix-100-API.json /comfyui/workflow.json

# Копируем конфиг extra_model_paths.yaml
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml

# Запускаем handler
CMD ["python", "-u", "/handler.py"]
