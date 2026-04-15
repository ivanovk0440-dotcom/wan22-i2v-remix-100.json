
FROM runpod/worker-comfyui:5.5.1-base
RUN sleep 20
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Клонируем кастомные ноды (все нужные для твоего workflow)
WORKDIR /comfyui/custom_nodes
RUN git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git
RUN git clone https://github.com/fannovel16/ComfyUI-Frame-Interpolation.git
RUN git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git
RUN git clone https://github.com/yolain/ComfyUI-Easy-Use.git

# Устанавливаем зависимости (gguf — для WanVideoWrapper)
RUN pip install --no-cache-dir opencv-python accelerate gguf

# Копируем handler и workflow
COPY handler.py /handler.py
COPY Wan22-I2V-Remix-100.json /comfyui/workflow.json

CMD ["python", "-u", "/handler.py"]
