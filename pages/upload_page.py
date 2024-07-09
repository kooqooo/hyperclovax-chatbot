import gradio as gr
import os
import shutil
import requests
import io

# 서버 URL
server_url = "http://127.0.0.1:8000/"

def post_file(audio):
    # url = server_url + 'files'
    url = server_url + 'process'
    original_filename = os.path.basename(audio)
    
    with open(audio, 'rb') as file:
        files = {'file': (original_filename, file, 'application/octet-stream')}
        response = requests.post(url, files=files)

    return f"Audio file saved as: {response.json()}"

# Gradio 인터페이스 생성
iface = gr.Interface(
    fn=post_file,
    inputs=gr.Audio(type="filepath"),
    outputs="text",
    title="Audio File Uploader",
    description="Upload an audio file to save it on the server with its original filename."
)

# 인터페이스 실행
iface.launch()