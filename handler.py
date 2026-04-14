import runpod
import subprocess
import time
import requests
import json
import base64
import os

comfy_process = None

def start_comfy():
    global comfy_process
    if comfy_process is None:
        print("Запуск ComfyUI...")
        comfy_process = subprocess.Popen(
            ["python", "/comfyui/main.py", "--listen", "0.0.0.0", "--port", "8188"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for i in range(30):
            try:
                requests.get("http://localhost:8188", timeout=2)
                print("ComfyUI готов!")
                return True
            except:
                print(f"Ожидание ComfyUI... {i+1}/30")
                time.sleep(2)
        print("Ошибка: ComfyUI не запустился")
        return False
    return True

def handler(job):
    print(f"Получен запрос: {job.get('id')}")
    
    if not start_comfy():
        return {"error": "ComfyUI failed to start"}
    
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
        print(f"Сохранено изображение: {img_name}")
    
    # ============================================
    # КЛЮЧЕВОЙ МОМЕНТ: ОТПРАВКА WORKFLOW
    # ============================================
    print("Отправка workflow в ComfyUI...")
    response = requests.post("http://localhost:8188/prompt", json={"prompt": workflow})
    
    if response.status_code != 200:
        return {"error": f"ComfyUI error: {response.text}"}
    
    prompt_id = response.json()['prompt_id']
    print(f"Prompt ID: {prompt_id}")
    
    # Ожидание результата (до 40 минут)
    print("Ожидание генерации видео...")
    for _ in range(1200):
        time.sleep(2)
        history_resp = requests.get(f"http://localhost:8188/history/{prompt_id}")
        
        if history_resp.status_code == 200:
            history = history_resp.json()
            if prompt_id in history:
                outputs = history[prompt_id]['outputs']
                print(f"Outputs: {json.dumps(outputs, indent=2)}")
                
                for node_id, node_output in outputs.items():
                    if 'videos' in node_output and node_output['videos']:
                        video = node_output['videos'][0]
                        video_url = f"http://localhost:8188/view?filename={video['filename']}&type=output"
                        print(f"Видео сгенерировано: {video_url}")
                        return {"status": "completed", "video_url": video_url}
                    
                    if 'images' in node_output and node_output['images']:
                        img = node_output['images'][0]
                        img_url = f"http://localhost:8188/view?filename={img['filename']}&type=output"
                        print(f"Изображение сгенерировано: {img_url}")
                        return {"status": "completed", "image_url": img_url}
    
    return {"error": "Generation timeout (40 minutes)"}

if __name__ == "__main__":
    print("Запуск RunPod Serverless Worker...")
    runpod.serverless.start({"handler": handler})
