from pathlib import Path
import torch
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from datetime import datetime

# Global variables
model_name = "jhgan/ko-sroberta-multitask"
model_kwargs = {'device': "cuda" if torch.cuda.is_available() else "cpu"}
encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
faiss_store_name = "./FAISS_INDEXES"

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def add_documents_to_faiss_index(new_documents: list[Document]):
    db = load_faiss_index(faiss_store_name)
    new_db = FAISS.from_documents(new_documents, embeddings)
    db.merge_from(new_db)
    db.save_local(faiss_store_name)

def faiss_inference(query: str, k: int = 1) -> list[str]:
    db = load_faiss_index(faiss_store_name)
    if db.index.ntotal < k:   # OutOfIndex 방지를 위한 k 설정
        k = db.index.ntotal
    return list(db.similarity_search(query, k=k)[x].page_content for x in range(k))

def get_retriever() -> VectorStoreRetriever:
    db = load_faiss_index(faiss_store_name)
    return db.as_retriever()

def load_faiss_index(index_path: str) -> FAISS:
    faiss_index = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return faiss_index

def init_faiss_index():
    tmp_doc = [Document(page_content="Start", metadata=dict(id=-1))]
    db = FAISS.from_documents(tmp_doc, embeddings)
    db.delete([db.index_to_docstore_id[0]])
    db.save_local(faiss_store_name)

# doc_id가 맞는 document의 ID를 추출하는 함수
def get_ids_by_doc_id(db_dict, target_doc_id):
    result_ids = []
    for doc_id, doc_info in db_dict.items():
        if doc_info.metadata['doc_id'] == target_doc_id:
            result_ids.append(doc_id)
    return result_ids

def delete_faiss_index(doc_id):
    try:
        db = load_faiss_index(faiss_store_name)
        del_docs = db.similarity_search_with_score("foo", filter=dict(doc_id=int(doc_id)), k=db.index.ntotal)
        result_ids = get_ids_by_doc_id(db.docstore._dict, int(doc_id))
        db.delete(result_ids)
        db.save_local(faiss_store_name)
    except Exception as e:
        raise Exception(f"Error: {e}")
    
def show_faiss_index():
    db = load_faiss_index(faiss_store_name)
    if db.index.ntotal==0:
        print("No data in the vector DB")
        return {}
    docs = db.similarity_search_with_score("", k=db.index.ntotal)
    for doc in docs:
        print(doc)
    
    return db.docstore._dict

def save_to_mongoDB(data, title=get_current_time(), created_date=get_current_time()) -> int:
    '''
    코드:
        mongoDB에 회의록 데이터 저장
    return:
        저장된 회의록 데이터의 id
    '''

def main():

    init_faiss_index()  # faiss index 초기화
    
    show_faiss_index()  # vectorDB 출력
    
    # 회의록 입력 예시: 테스트를 위한 예시 입력 데이터입니다.
    doc_list = [Document(page_content="foo", metadata=dict(doc_id=1)), Document(page_content="bar", metadata=dict(doc_id=1)),
                Document(page_content="var", metadata=dict(doc_id=2)), Document(page_content="bar", metadata=dict(doc_id=2)),
                Document(page_content="maxseats", metadata=dict(doc_id=3)), Document(page_content="bar", metadata=dict(doc_id=3))]
    add_documents_to_faiss_index(doc_list)
    
    show_faiss_index()
    
    delete_faiss_index(doc_id=2) # doc_id가 2인 문서 삭제 

    show_faiss_index() #출력 확인

if __name__ == "__main__":
    main()