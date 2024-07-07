import gradio as gr
import os
import shutil
import requests
import io

# 서버 URL
server_url = "http://127.0.0.1:8000/"

# 오디오 파일을 저장할 디렉토리 설정
UPLOAD_DIR = "./"

# 디렉토리가 없으면 생성
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def get_stt(audio):
    url = server_url + 'files'
    original_filename = os.path.basename(audio)
    
    with open(audio, 'rb') as file:
        files = {'file': (original_filename, file, 'application/octet-stream')}
        response = requests.post(url, files=files)

    return f"Audio file saved as: {response.json()}"

def save_audio(audio):
    if audio is None:
        return "No audio file uploaded."
    
    # 원본 파일 이름 추출
    original_filename = os.path.basename(audio)
    
    # # 파일 저장 경로
    # save_path = os.path.join(UPLOAD_DIR, original_filename)
    
    # # 파일 이름 중복 확인 및 처리
    # counter = 1
    # while os.path.exists(save_path):
        # name, ext = os.path.splitext(original_filename)
        # new_filename = f"{name}_{counter}{ext}"
    #     save_path = os.path.join(UPLOAD_DIR, new_filename)
    #     counter += 1
    
    # 파일 저장
    # shutil.copy(audio, save_path)
    response = requests.post(upload_url, audio)
    
    return f"Audio file saved as: {os.path.basename(save_path)}"

# Gradio 인터페이스 생성
iface = gr.Interface(
    fn=get_stt,
    inputs=gr.Audio(type="filepath"),
    outputs="text",
    title="Audio File Uploader",
    description="Upload an audio file to save it on the server with its original filename."
)

# 인터페이스 실행
iface.launch()



# import requests

# def upload_file(file_path, upload_url):
#     # 업로드할 파일 열기
#     with open(file_path, 'rb') as file:
#         # 파일 이름 추출
#         file_name = file_path.split('/')[-1]
        
#         # 파일과 함께 전송할 데이터
#         files = {'file': (file_name, file, 'application/octet-stream')}
        
#         # 추가적인 데이터가 필요한 경우 (선택사항)
#         data = {'key': 'value'}
        
#         # POST 요청 보내기
#         response = requests.post(upload_url, files=files, data=data)
    
#     # 응답 확인
#     if response.status_code == 200:
#         print("File uploaded successfully!")
#         print("Server response:", response.text)
#     else:
#         print(f"Failed to upload file. Status code: {response.status_code}")
#         print("Server response:", response.text)

# # 사용 예시
# file_path = '/path/to/your/file.txt'  # 업로드할 파일의 경로
# upload_url = 'http://example.com/upload'  # 파일을 업로드할 서버의 URL

# upload_file(file_path, upload_url)