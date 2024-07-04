""" Author: @maxseats
ㅁㄴㅇㄹAPI 문서는 아래를 참고하세요.
ㅁㄴㅇㄹhttps://api.ncloud-docs.com/docs/clovastudio-chatcompletions


[API 요청 실험]

"""
import requests
import urllib.parse
from typing import List, Optional
import json
from datetime import datetime

from vectordb_manager import show_faiss_index

# 서버 URL
server_url = "http://127.0.0.1:8000/"

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_answer(query: str) -> str:
    url = server_url + 'answer'
    response = requests.get(url, params={"query": query})
    return response.json()

def put_document(data_path, title: str = get_current_time(), created_date: str = get_current_time()):
    url = server_url + 'document'
    
    # 요청에 필요한 데이터
    data = {"data_path": data_path, "title": title, "created_date": created_date}
    
    # 요청 보내기
    headers = {"Content-Type": "application/json", "data": json.dumps(data)}
    response = requests.put(url, headers=headers)

    # 응답 확인
    return response.json()

def delete_document(doc_id):
    url = server_url + 'document'
    headers = {"Content-Type": "application/json", "doc_id": str(doc_id)}
    response = requests.delete(url, headers=headers)
    return response.json()

def delete_initialization():
    url = server_url + 'initalization'
    response = requests.delete(url)
    return response.json()


if __name__ == "__main__":
    
    # DB 초기화
    delete_initialization()
    print('1: '); show_faiss_index(); print()
    
    # RAG 질의응답 request
    query = "파이썬은 어디에서 관리하는가?"
    result = get_answer(query)
    print(result)

    '''
    회의록 데이터 PUT request (DB에 저장)
    회의록 txt파일 경로, title, created_date를 입력해줍니다.
    title, created_date : 미 입력시 현재 시간으로 지정됩니다.
    '''
    put_document(data_path="./wiki_python.txt", title="Maxseats Test", created_date="2023-07-02 12:34:56")
    put_document(data_path="./wiki_python.txt", title="Maxseats Test")
    put_document(data_path="./wiki_python.txt")
    print('2: '); show_faiss_index(); print()
    
    # 회의록 DELETE test
    # doc_id를 참조해서 Delete를 수행합니다.
    delete_document('1')
    print('3: '); show_faiss_index(); print()