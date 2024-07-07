import gradio as gr
import os
import shutil

# 오디오 파일을 저장할 디렉토리 설정
UPLOAD_DIR = "./"

# 디렉토리가 없으면 생성
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_audio(audio):
    if audio is None:
        return "No audio file uploaded."
    
    # 원본 파일 이름 추출
    original_filename = os.path.basename(audio)
    
    # 파일 저장 경로
    save_path = os.path.join(UPLOAD_DIR, original_filename)
    
    # 파일 이름 중복 확인 및 처리
    counter = 1
    while os.path.exists(save_path):
        name, ext = os.path.splitext(original_filename)
        new_filename = f"{name}_{counter}{ext}"
        save_path = os.path.join(UPLOAD_DIR, new_filename)
        counter += 1
    
    # 파일 저장
    shutil.copy(audio, save_path)
    
    return f"Audio file saved as: {os.path.basename(save_path)}"

# Gradio 인터페이스 생성
iface = gr.Interface(
    fn=save_audio,
    inputs=gr.Audio(type="filepath"),
    outputs="text",
    title="Audio File Uploader",
    description="Upload an audio file to save it on the server with its original filename."
)

# 인터페이스 실행
iface.launch()