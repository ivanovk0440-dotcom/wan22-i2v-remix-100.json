FROM atumn/runpod-wan:latest

# Копируем только handler и workflow (ComfyUI уже внутри)
COPY handler.py /handler.py
COPY Wan22-I2V-Remix-100-API.json /workflow.json

CMD ["python", "-u", "/handler.py"]
