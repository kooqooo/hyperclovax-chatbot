""" Author: @maxseats
서버에게 RAG 질의응답, 회의록 데이터 CRUD 요청을 보내는 코드입니다.
모든 요청은 /docs 엔드포인트에서 실험해볼 수 있어요. (http://127.0.0.1:8000/docs)

[API 요청]
DB 초기화, RAG 질의응답, 회의록 PUT, 회의록 DELETE 순으로 요청을 보내는 코드에요.
각 과정에 get_showdb()를 통해 DB의 상태를 확인할 수 있어요.
"""

import os
import json
from datetime import datetime
from pprint import pprint

import pytz
import requests

from backend.meeting_model import Meeting
from mongodb_manager import show_mongoDB_data
from vectordb_manager import show_faiss_index
from utils.seoul_time import seoul_now, datetime_to_str, str_to_datetime

# 서버 URL
server_url = "http://127.0.0.1:8000/"

def get_current_time():
    return datetime.now(tz=pytz.timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")

def get_answer(query: str) -> str:
    url = server_url + 'answer'
    response = requests.get(url, params={"query": query})
    return response.json()

def put_document(uuid, txt_path, title: str=None, created_date: str = datetime_to_str(seoul_now())):
    url = server_url + 'document'
    
    if title is None:
        title = os.path.basename(txt_path)
    
    # 요청에 필요한 데이터
    data = {"uuid": uuid, "txt_path": txt_path, "title": title, "created_date": created_date}
    
    # 요청 보내기
    headers = {"Content-Type": "application/json", "data": json.dumps(data)}
    response = requests.put(url, headers=headers)

    # 응답 확인
    return response.json()

def put_documents(transcript: str, meeting_id: str, time: str = datetime_to_str(seoul_now())) -> dict:
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
    url = server_url + 'initialization'
    response = requests.delete(url)
    return response.json()

def get_showdb():
    url = server_url + 'showdb'
    response = requests.get(url)
    # print(response.json())
    
    data = response.json()
    faiss_data = data.get("FAISS")
    mongodb_data = data.get("MongoDB")
    
    pprint(faiss_data)
    print()
    pprint(mongodb_data)
    return faiss_data, mongodb_data

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
    
    # DB 초기화
    delete_initialization()
    print('1: '); get_showdb(); print()
    
    # 
    
    
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
    
    
    
    
    
    
    
    # DB 초기화
    delete_initialization()
    print('1: '); get_showdb(); print()
    
    ## 나눠서 하는 방식
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
    response = put_documents(transcript, meeting_id, now_str)
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
