""" Author: @kooqooo
API 문서는 아래를 참고하세요.
https://api.ncloud-docs.com/docs/clovastudio-chatcompletions


[실행 속도 실험]
Python 3.12.4 버전의 내장 time 모듈을 사용하여 8회 실험을 했습니다.
결과는 8회 실험의 총합입니다. maxTokens와 prompt를 바꾸며 실행했습니다.
1. list에 모든 내용을 저장하는 경우: 72.09초
2. deque에 maxlen=4를 설정하여 저장하는 경우: 74.3초
결론: 큰 차이가 없음. list를 사용하는 것이 더 편리함.
"""

from ast import literal_eval

import requests


class CompletionExecutor:
    def __init__(
        self,
        api_key,
        api_key_primary_val,
        request_id,
        test_app_id,
        host="https://clovastudio.stream.ntruss.com"
    ) -> None:
        self.__host = host
        self.__api_key = api_key
        self.__api_key_primary_val = api_key_primary_val
        self.__request_id = request_id
        self.__test_app_id = test_app_id

    def execute_all(self, completion_request):
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self.__api_key,
            "X-NCP-APIGW-API-KEY": self.__api_key_primary_val,
            # "X-NCP-CLOVASTUDIO-REQUEST-ID": self.__request_id, # 없어도 작동 잘함
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }
        with requests.post(
            f"{self.__host}/testapp/v1/chat-completions/{self.__test_app_id}",
            headers=headers,
            json=completion_request,
            stream=True,
        ) as r:
            result = []
            for idx, line in enumerate(r.iter_lines()):
                if line:
                    print(idx, end=": ")
                    print(line.decode("utf-8"))
                    result.append(line.decode("utf-8"))
        return result

    def execute(self, completion_request):
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self.__api_key,
            "X-NCP-APIGW-API-KEY": self.__api_key_primary_val,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self.__request_id, # 없어도 작동 가능
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }
        with requests.post(
            f"{self.__host}/testapp/v1/chat-completions/{self.__test_app_id}",
            headers=headers,
            json=completion_request,
            stream=True,
        ) as r:
            result = []
            for line in r.iter_lines():
                if line:
                    result.append(line.decode("utf-8"))
        return result[-4]


def parse_response(response: str) -> str:
    """
    실제 message의 content를 반환합니다.
    """
    response_dict = literal_eval(response[5:])  # "data:" 제거
    return response_dict["message"]["content"].replace("\\n", "\n")


if __name__ == "__main__":
    import os
    
    from dotenv import load_dotenv
    
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    API_KEY_PRIMARY_VAL = os.getenv("API_KEY_PRIMARY_VAL")
    REQUEST_ID = os.getenv("REQUEST_ID")
    TEST_APP_ID = os.getenv("TEST_APP_ID")

    preset_text = [
        {"role": "system", "content": "사용자의 질문에 답변합니다."},
        {"role": "user", "content": "경기도 용인시 기흥구 보정동 근처 맛집 추천해줘"}, # <- 맛없는 거 추천해줌
    ]

    request_data = {
        "messages": preset_text,
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.1,  # 0으로 설정 불가
        "repeatPenalty": 5.0,
        "stopBefore": [],
        "includeAiFilters": True,
        "seed": 0,
    }

    completion_executor = CompletionExecutor(
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=REQUEST_ID,
        test_app_id=TEST_APP_ID,
    )
    
    response = completion_executor.execute(request_data)  # 대략 10~20초 정도 소요됨
    print(response)
    print(parse_response(response))
