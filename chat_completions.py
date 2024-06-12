""" Author: @kooqooo
API 문서는 아래를 참고하세요.
https://api.ncloud-docs.com/docs/clovastudio-chatcompletions
"""

import requests

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id, url_postfix):
        self.__host = host
        self.__api_key = api_key
        self.__api_key_primary_val = api_key_primary_val
        self.__request_id = request_id
        self.__url_postfix = url_postfix

    def execute(self, completion_request):
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self.__api_key,
            "X-NCP-APIGW-API-KEY": self.__api_key_primary_val,
            # "X-NCP-CLOVASTUDIO-REQUEST-ID": self.__request_id, # 없어도 작동 잘함
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }
        with requests.post(
            self.__host + self.__url_postfix,
            headers=headers,
            json=completion_request,
            stream=True,
        ) as r:
            for line in r.iter_lines():
                if line:
                    print(line.decode("utf-8"))


if __name__ == "__main__":
    import yaml

    with open("secrets.yaml", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    completion_executor = CompletionExecutor(**config["test"])

    preset_text = [
        {"role": "system", "content": "사용자의 질문에 답변합니다."},
        {"role": "user", "content": "보정동 근처 맛집 추천해줘"}, # <- 맛없는 거 추천해줌
    ]

    request_data = {
        "messages": preset_text,
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.1,
        "repeatPenalty": 5.0,
        "stopBefore": [],
        "includeAiFilters": True,
        "seed": 0,
    }

    print(preset_text)
    completion_executor.execute(request_data)
    