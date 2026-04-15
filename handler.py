import runpod
import requests
import time
import json
import base64
import subprocess
import os

comfy_process = None

def start_comfy():
    global comfy_process
    if comfy_process is None:
        print("Starting ComfyUI...")
        comfy_process = subprocess.Popen(
            ["python", "/comfyui/main.py", "--listen", "0.0.0.0", "--port", "8188"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Ждём запуска ComfyUI (до 60 секунд)
        for i in range(30):
            try:
                requests.get("http://localhost:8188", timeout=2)
                print("ComfyUI is ready!")
                return True
            except:
                print(f"Waiting for ComfyUI... {i+1}/30")
                time.sleep(2)
        print("Error: ComfyUI failed to start")
        return False
    return True

def handler(event):
    print("Worker Start")
    
    # Запускаем ComfyUI если ещё не запущен
    if not start_comfy():
        return {"error": "ComfyUI failed to start"}
    
    input_data = event['input']
    workflow = input_data.get('workflow')
    images = input_data.get('images', [])
    
    if not workflow:
        return {"error": "Workflow is required"}
    
    # Сохраняем изображения
    for img in images:
        img_name = img.get('name', 'image.jpg')
        img_data = base64.b64decode(img.get('image'))
        with open(f"/comfyui/input/{img_name}", "wb") as f:
            f.write(img_data)
        print(f"Saved image: {img_name}")
    
    # Отправляем workflow в ComfyUI
    print("Sending workflow to ComfyUI...")
    response = requests.post("http://localhost:8188/prompt", json={"prompt": workflow})
    
    if response.status_code != 200:
        return {"error": f"ComfyUI error: {response.text}"}
    
    prompt_id = response.json()['prompt_id']
    print(f"Prompt ID: {prompt_id}")
    
    # Ждём результат
    for _ in range(600):
        time.sleep(2)
        history = requests.get(f"http://localhost:8188/history/{prompt_id}").json()
        
        if prompt_id in history:
            outputs = history[prompt_id]['outputs']
            print(f"Outputs: {list(outputs.keys())}")
            
            for node_id, node_output in outputs.items():
                if 'videos' in node_output and node_output['videos']:
                    video = node_output['videos'][0]
                    video_url = f"http://localhost:8188/view?filename={video['filename']}&type=output"
                    print(f"Video generated: {video_url}")
                    return {"status": "completed", "video_url": video_url}
                
                if 'images' in node_output and node_output['images']:
                    img = node_output['images'][0]
                    img_url = f"http://localhost:8188/view?filename={img['filename']}&type=output"
                    print(f"Image generated: {img_url}")
                    return {"status": "completed", "image_url": img_url}
    
    return {"error": "Generation timeout (20 minutes)"}

if __name__ == '__main__':
    print("Starting RunPod Serverless Worker...")
    runpod.serverless.start({'handler': handler})
