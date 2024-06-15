""" Author: @kooqooo
실행 안되는 코드임
"""

import yaml
from langchain_community.embeddings import ClovaEmbeddings

with open("secrets.yaml", encoding="utf-8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)   

clova_emb_api_key = config["test"]["api_key"]
clova_emb_apigw_api_key = config["test"]["api_key_primary_val"]
app_id = config["test"]["request_id"]
# clova_emb_api_key = config["client_id"]           # 이거 사용시 Unathorized Error 발생
# clova_emb_apigw_api_key = config["client_secret"] # 이거 사용시 Unathorized Error 발생

# 참고 문서
# https://api.python.langchain.com/en/latest/embeddings/langchain_community.embeddings.clova.ClovaEmbeddings.html#langchain_community.embeddings.clova.ClovaEmbeddings
embeddings = ClovaEmbeddings(
    clova_emb_api_key=clova_emb_api_key,
    clova_emb_apigw_api_key=clova_emb_apigw_api_key,
    app_id=app_id
)

query_text = "This is a test query."
query_result = embeddings.embed_query(query_text)

document_text = "This is a test document."
document_result = embeddings.embed_documents([document_text])