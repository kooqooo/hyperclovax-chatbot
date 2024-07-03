import requests
import urllib.parse
from typing import List, Optional
import json

# 서버 URL
server_url = "http://127.0.0.1:8000/"


def get_answer(query: str) -> str:
    url = server_url + 'answer'
    response = requests.get(url, params={"query": query})
    return response

def put_document(data_path, title: Optional[str], created_date: Optional[str]):
    url = server_url + 'document'
    
    # 요청에 필요한 데이터
    data = {
        "data_path": data_path,
        "title": title,
        "created_date": created_date
    }
    
    # 요청 보내기
    headers = {"Content-Type": "application/json", "data": json.dumps(data)}
    response = requests.put(url, headers=headers)

    # 응답 확인
    print(response.status_code)
    print(response)

if __name__ == "__main__":
    # query = "파이썬을 어디에서 관리하는가?"
    # query = "출처가 어디인가?"
    # result = get_answer(query).json()
    # print(result)

    put_document("./wiki_python.txt", "Maxseats Test", "2023-07-02 12:34:56")