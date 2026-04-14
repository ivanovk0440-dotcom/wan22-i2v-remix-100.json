import runpod
import subprocess
import time
import requests
import json
import base64

# Запускаем ComfyUI как фоновый процесс
comfy_process = None

def start_comfy():
    global comfy_process
    if comfy_process is None:
        comfy_process = subprocess.Popen(
            ["python", "/comfyui/main.py", "--listen", "0.0.0.0", "--port", "8188"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Ждём запуска ComfyUI
        for _ in range(30):
            try:
                requests.get("http://localhost:8188", timeout=2)
                print("ComfyUI готов")
                break
            except:
                print("Ожидание ComfyUI...")
                time.sleep(1)

def handler(job):
    """
    Хендлер для RunPod Serverless
    """
    # Убеждаемся что ComfyUI запущен
    if comfy_process is None:
        start_comfy()
    
    # Получаем входные данные
    job_input = job.get("input", {})
    workflow = job_input.get("workflow")
    images = job_input.get("images", [])
    
    if not workflow:
        return {"error": "Workflow is required"}
    
    # Сохраняем изображения
    for img in images:
        img_name = img.get('name', 'image.jpg')
        img_data = base64.b64decode(img.get('image'))
        with open(f"/comfyui/input/{img_name}", "wb") as f:
            f.write(img_data)
    
    # Отправляем workflow в ComfyUI
    response = requests.post("http://localhost:8188/prompt", json={"prompt": workflow})
    
    if response.status_code != 200:
        return {"error": f"ComfyUI error: {response.text}"}
    
    prompt_id = response.json()['prompt_id']
    print(f"Prompt ID: {prompt_id}")
    
    # Ждём результат (до 40 минут = 1200 попыток × 2 секунды)
    for _ in range(1200):
        time.sleep(2)
        history = requests.get(f"http://localhost:8188/history/{prompt_id}").json()
        
        if prompt_id in history:
            outputs = history[prompt_id]['outputs']
            
            # Ищем видео или изображение
            for node_id, node_output in outputs.items():
                if 'videos' in node_output and node_output['videos']:
                    video = node_output['videos'][0]
                    video_url = f"http://localhost:8188/view?filename={video['filename']}&type=output"
                    return {"status": "completed", "video_url": video_url}
                if 'images' in node_output and node_output['images']:
                    img = node_output['images'][0]
                    img_url = f"http://localhost:8188/view?filename={img['filename']}&type=output"
                    return {"status": "completed", "image_url": img_url}
    
    # Таймаут после 40 минут
    return {"error": "Timeout: generation took more than 40 minutes"}

# Запускаем серверлес-воркер
if __name__ == "__main__":
    start_comfy()
    print("Запуск RunPod Serverless Worker...")
    runpod.serverless.start({"handler": handler})