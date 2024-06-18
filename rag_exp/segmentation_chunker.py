from ast import literal_eval
import http.client
import json

from tqdm import tqdm
import requests

from preprocessing_from_html import main as preprocessing_main


class SegmentationExecutor:
    def __init__(self, api_key, api_key_primary_val, request_id, test_app_id, host="clovastudio.apigw.ntruss.com"):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id
        self._test_app_id = test_app_id
 
    def _send_request(self, completion_request):
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-NCP-CLOVASTUDIO-API-KEY": self._api_key,
            "X-NCP-APIGW-API-KEY": self._api_key_primary_val,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id, # 없어도 작동 잘함
        }
 
        conn = http.client.HTTPSConnection(self._host)
        conn.request(
            "POST",
            f"/testapp/v1/api-tools/segmentation/{self._test_app_id}",
            json.dumps(completion_request),
            headers
        )
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding="utf-8"))
        conn.close()
        return result
 
    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res["status"]["code"] == "20000":
            return res["result"]["topicSeg"]
        else:
            return "Error"


if __name__ == "__main__":
    import yaml

    with open("../secrets.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    segmentation_executor = SegmentationExecutor(**config["test"])
 
    chunked_html = []
    clovastudiodatas_flattened = preprocessing_main()
    
    for htmldata in tqdm(clovastudiodatas_flattened):
        request_json_string = f"""{{
            "postProcessMaxSize": 100,
            "alpha": 1.5,
            "segCnt": -1,
            "postProcessMinSize": 0,
            "text": {json.dumps(htmldata.page_content, ensure_ascii=False)},
            "postProcess": false
        }}"""

        request_data = json.loads(request_json_string, strict=False)
        response_data = segmentation_executor.execute(request_data)
        # 반환된 각 문단에 대해 source(주소) 포함하여 chunked_documents에 추가
        for paragraph in response_data:
            chunked_document = {
                "source": htmldata.metadata["source"],
                "text": paragraph
            }
            chunked_html.append(chunked_document)
 
    print(len(chunked_html))