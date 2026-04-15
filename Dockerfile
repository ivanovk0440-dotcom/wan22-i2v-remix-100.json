FROM runpod/worker-comfyui:5.5.1-base

# Ждём сеть (критически важно для git clone)
RUN sleep 30

# Установка gt и системных зависимостей
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей для WanVideoWrapper
RUN pip install --no-cache-dir opencv-python accelerate gguf runpod requests

# Клонирование кастомных нод с приоритетом WanVideoWrapper
WORKDIR /comfyui/custom_nodes

# Попытка 1: Прямое клонирование
RUN git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git || \
    git clone https://gitcode.com/GitHub_Trending/co/ComfyUI-WanVideoWrapper.git || \
    echo "WARNING: Could not clone WanVideoWrapper"

# Если клонирование не удалось, используем альтернативный форк
RUN if [ ! -d "ComfyUI-WanVideoWrapper" ]; then \
        git clone https://github.com/sienadrayy/ComfyUI-WanVideoWrapper.git || \
        git clone https://github.com/siraxe/ComfyUI-WanVideoWrapper_QQ.git; \
    fi

# Клонирование остальных нод (опционально)
RUN git clone https://github.com/fannovel16/ComfyUI-Frame-Interpolation.git || true
RUN git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git || true
RUN git clone https://github.com/yolain/ComfyUI-Easy-Use.git || true
RUN git clone https://github.com/kijai/ComfyUI-KJNodes.git || true

# Установка зависимостей для WanVideoWrapper
RUN if [ -d "ComfyUI-WanVideoWrapper" ]; then \
        cd ComfyUI-WanVideoWrapper && pip install --no-cache-dir -r requirements.txt || true; \
    fi

# Копирование и handler и workflow
COPY handler.py /handler.py
COPY Wan22-I2V-Remix-100.json /comfyui/workflow.json

# Запуск handler
CMD ["python", "-u", "/handler.py"]
