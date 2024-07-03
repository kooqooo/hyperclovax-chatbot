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

def delete_faiss_index(id):
    
    '구현 중입니다. 이 함수는 아직 미완성입니다.'
    
    tmp_doc = [Document(page_content="Start", metadata=dict(id=-1))]
    db = FAISS.from_documents(tmp_doc, embeddings)
    db.delete([db.index_to_docstore_id[0]])
    db.save_local(faiss_store_name)

def show_faiss_index():
    db = load_faiss_index(faiss_store_name)
    print(db.docstore._dict, '\n\n')
    
    return db.docstore._dict

def save_to_mongoDB(data, title=get_current_time(), created_date=get_current_time()) -> int:
    # mongoDB에 저장하는 코드 필요
    
    '''
    코드 작성 예정
    
    저장된 회의록 데이터의 id를 return
    '''

def main():
    def _print(docs):
        for idx, doc in enumerate(docs):
            score = None
            this = '->' if idx == 0 else '  '
            if type(doc) == tuple:
                doc, score = doc
            print(f"{this} content : {doc.page_content}")
            print(f"{this} metadata : {doc.metadata}") if doc.metadata else None
            print(f"{this} score : {score}") if score is not None else None
            print()
        print()


    data_path = "./wiki_python.txt"
    
    

    # TextLoader 사용하여 FAISS 객체를 생성하는 방식
    init_faiss_index()
    
    show_faiss_index() # 1
    
    doc_list = [Document(page_content="foo", metadata=dict(doc_id=1)), Document(page_content="bar", metadata=dict(doc_id=2))]
    add_documents_to_faiss_index(doc_list)
    
    
    show_faiss_index() # 2
    
    init_faiss_index()

    show_faiss_index() # 3
    
    
    # query = "파이썬을 어디에서 관리하는가?"
    # faiss_result = faiss_inference(query, k=1)
    # print(f"/** <{query}>와 유사도가 가장 높은 답은?? **/")
    # print(faiss_result)


    db = FAISS.load_local(faiss_store_name, embeddings, allow_dangerous_deserialization=True)
    print(help(db.delete))

    # # TextLoader의 load_and_split 메소드를 사용하는 방식
    # split_docs = TextLoader(data_path, encoding='utf-8').load_and_split(character_splitter) # 파이썬 위키백과 문서
    # # # Print the split documents
    # # print(*[split_doc.page_content for split_doc in split_docs], sep='\n\n')
    # for idx, split_doc in enumerate(split_docs):
    #     split_docs[idx].metadata['created_date'] = "1970-01-01"
    #     print(idx, ":", split_doc.page_content, end="\n\n")
    
    # chroma_db = Chroma.from_documents(split_docs, embeddings)
    # # print(f"{type(chroma_db.embeddings) = }")
    # print()

    # query = "파이썬을 어디에서 관리하는가?"
    # print(f"/** <{query}>와 유사도가 높은 답은 '->'로 표시 **/")
    # _print(chroma_db.similarity_search_with_score(query))
    # _print(chroma_db.similarity_search_with_relevance_scores(query))

    
    # # 텍스트를 직접 넣어서 Chroma 객체를 생성하는 방식
    # texts = ["안녕하세요", "오늘 날씨가 좋네요"]
    # chroma_db = Chroma.from_texts(texts, embeddings)
    # # print(f"{chroma_db.embeddings = }")
    # query = "반갑습니다"
    # print(f"/** <{query}>와 유사도가 높은 답은 '->'로 표시 **/")
    # _print(chroma_db.similarity_search_with_score(query, k=2))  # Cosine Distance, 0~2 사이의 값, 작을수록 유사도가 높음
    # _print(chroma_db.similarity_search_with_relevance_scores(query, k=2))  # Relevance Score, 0~1 사이의 값, 클수록 유사도가 높음

    
    # # Retriver를 사용하는 방식
    # retriever = get_retriever()
    # retriever_result = retriever.invoke(query)[0]
    # print(retriever_result)


if __name__ == "__main__":
    main()