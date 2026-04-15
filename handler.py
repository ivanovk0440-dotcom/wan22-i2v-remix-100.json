import runpod
import requests
import time
import json
import base64
import os

def handler(event):
    print("Worker Start")
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
    for _ in range(600):  # 20 минут максимум
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
