import requests
import urllib.parse

# 서버 URL
server_url = "http://127.0.0.1:8000/"


def get_answer(query: str) -> str:
    url = server_url + 'answer'
    response = requests.get(url, params={"query": query})
    return response

if __name__ == "__main__":
    # query = "파이썬을 어디에서 관리하는가?"
    query = "출처가 어디인가?"
    result = get_answer(query).json()
    print(result)
