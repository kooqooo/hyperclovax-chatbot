import requests
import json
from datetime import datetime

from backend.meeting_model import Meeting
from utils.seoul_time import seoul_now, datetime_to_str, str_to_datetime


# 서버 URL
server_url = "http://127.0.0.1:8000/"

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_answer(query: str) -> str:
    url = server_url + 'answer'
    response = requests.get(url, params={"query": query})
    return response.json()

def put_document(transcript: str, meeting_id: str, time: str = datetime_to_str(seoul_now())) -> dict:
    url = server_url + 'documents'
    
    # 요청에 필요한 데이터
    data = {"transcript": transcript, "time": time, "meeting_id": meeting_id}
    
    # 요청 보내기
    headers = {"Content-Type": "application/json", "data": json.dumps(data)}
    response = requests.put(url, headers=headers)

    # 응답 확인
    return response.json()

def delete_document(doc_id: str):
    url = server_url + 'documents'
    headers = {"Content-Type": "application/json", "doc_id": doc_id}
    response = requests.delete(url, headers=headers)
    return response.json()

def delete_initialization():
    url = server_url + 'initalization'
    response = requests.delete(url)
    return response.json()

def request_create_meeting(
    file_id: str,
    transcript: str,
    time: str = datetime_to_str(seoul_now())
) -> dict:
    
    url = server_url + 'meetings/'
    time_datetime = str_to_datetime(time)
    meeting = Meeting(
        title=time,
        transcript=transcript,
        audio_file_id=file_id,
        # faiss_file_id=id,
        created_at=time_datetime
    )
    request_body = meeting.model_dump_json()
    response = requests.post(url, data=request_body)
    return response.json()

def request_create_document(
    meeting_id: str,
    transcript: str,
    time: str = datetime_to_str(seoul_now())
) -> dict:
    
    url = server_url + 'documents'
    
    response = requests.post(url)
    return response.json()

def upload_audio_file(file_path: str) -> str:
    url = server_url + 'files'
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file, 'application/octet-stream')}
        response = requests.post(url, files=files)
    return response.json()

def request_segment_audio(uuid: str):
    url = server_url + 'segment/' + uuid
    response = requests.post(url)
    return response.json()

def request_stt(uuid: str):
    url = server_url + 'stt/' + uuid
    response = requests.get(url)
    return response.json()


if __name__ == "__main__":
    import os
    from config import PATH
    
    # 오디오 파일 업로드
    response = upload_audio_file(os.path.join(PATH, '디스코드 회의.mp3'))
    uuid = response['uuid']
    file_id = response['file_id']
    print(f"Audio file uploaded with UUID: {uuid}, File ID: {file_id}.")
    
    # 오디오 파일 세그멘트
    response = request_segment_audio(uuid)
    num_files = response['num_files']
    print(f"Audio file segmented into {num_files} files.")
    
    # STT 요청
    response = request_stt(uuid)
    transcript = response['transcript']
    print(f"Transcript: {transcript}")
    
    now = seoul_now()
    now_str = datetime_to_str(now)

    # 회의기록 MongoDB에 업로드
    response = request_create_meeting(file_id, transcript, now_str)
    meeting = response
    print(f"Meeting created meeting: {meeting}")
    meeting_id = meeting['_id']
    print(f"Meeting created with ID: {meeting_id}")

    # FAISS 인덱스 초기화 or 추가
    response = put_document(transcript, meeting_id, now_str)
    print(f"Document created with response: {response}")

    # 질문 1
    query = "어떤 것을 이용해서 우리가 라벨링을 할 수 있을까요?" # 기대 답변: 저작도구
    response = get_answer(query)
    result = response['result']
    print(f"Answer to '{query}': {result}")
    
    # 질문 2
    query = "라벨링을 위한 도구는 무엇인가요?" # 기대 답변: 저작도구
    response = get_answer(query)
    result = response['result']
    print(f"Answer to '{query}': {result}")
    
    # 질문 3
    query = "오늘 해야 할 일이 무엇인가요?" # 기대 답변: 위스파 모델 다 공부해 오는 거
    response = get_answer(query)
    result = response['result']
    print(f"Answer to '{query}': {result}")