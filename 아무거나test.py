from datetime import datetime
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# # 예제 split_docs 리스트 (실제 코드는 다를 수 있음)
# split_docs = [{'metadata': {}} for _ in range(5)]  # 임의의 예제 리스트

# 현재 시간 가져오기

print(current_time, type(current_time))
# # split_docs의 각 항목에 현재 시간 설정하기
# for idx in range(len(split_docs)):
#     split_docs[idx]['metadata']['created_date'] = current_time

# # 예제 출력
# for doc in split_docs:
#     print(doc)











# from pathlib import Path

# import torch
# from langchain_community.document_loaders import TextLoader
# from langchain_community.vectorstores.chroma import Chroma
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface.embeddings import HuggingFaceEmbeddings
# from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings
# from langchain_core.vectorstores import VectorStoreRetriever
# from langchain_core.documents import Document


# # Global variables
# model_name = "jhgan/ko-sroberta-multitask"
# model_kwargs = {'device': "cuda" if torch.cuda.is_available() else "cpu"}
# encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity
# embeddings = HuggingFaceEmbeddings(
#     model_name=model_name,
#     model_kwargs=model_kwargs,
#     encode_kwargs=encode_kwargs
# )
# faiss_store_name = "./FAISS_INDEXES"


# list_of_documents = [
#     Document(page_content="foo", metadata=dict(page=1)),
#     Document(page_content="bar", metadata=dict(page=1)),
#     Document(page_content="foo", metadata=dict(page=2)),
#     Document(page_content="barbar", metadata=dict(page=2)),
#     Document(page_content="foo", metadata=dict(page=3)),
#     Document(page_content="bar burr", metadata=dict(page=3)),
#     Document(page_content="foo", metadata=dict(page=4)),
#     Document(page_content="bar bruh", metadata=dict(page=4)),
# ]
# db = FAISS.from_documents(list_of_documents, embeddings)
# # results_with_scores = db.similarity_search_with_score("foo")
# # for doc, score in results_with_scores:
# #     print(f"Content: {doc.page_content}, Metadata: {doc.metadata}, Score: {score}")
    
    
# # merge    
# db1 = FAISS.from_texts(["foo"], embeddings)
# db2 = FAISS.from_texts(["bar"], embeddings)

# print(db1.docstore._dict)

# print(db2.docstore._dict)


# print(db1.merge_from(db2))  # None

# print(db1.docstore._dict)
