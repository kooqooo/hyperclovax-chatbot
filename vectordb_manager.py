from pathlib import Path

import torch
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings

from text_splitters import character_splitter

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


def make_faiss_index(path: str | Path):
    split_docs = TextLoader(path, encoding='utf-8').load_and_split(character_splitter)
    new_db = FAISS.from_documents(split_docs, embeddings)
    new_db.save_local(faiss_store_name)


def faiss_inference(query, k=1):
    db = FAISS.load_local(faiss_store_name, embeddings, allow_dangerous_deserialization=True)
    # results = query.split("\n")
    # final_result = []
    # for i in results:
    #     docs = new_db.similarity_search(i, k=4)
    #     page_contents = [final_result.append(doc.page_content) for doc in docs]
    # # 중복된 문장 제거
    # final_result = list(set(final_result))
    # return final_result
    if k == 1:
        return db.similarity_search(query, k=1)[0].page_content
    else:
        return list(db.similarity_search(query, k=k)[x].page_content for x in range(k))


def get_retriever():
    db = FAISS.load_local(faiss_store_name, embeddings, allow_dangerous_deserialization=True)
    return db.as_retriever()


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
    # TextLoader의 load_and_split 메소드를 사용하는 방식
    split_docs = TextLoader(data_path, encoding='utf-8').load_and_split(character_splitter) # 파이썬 위키백과 문서
    # # Print the split documents
    # print(*[split_doc.page_content for split_doc in split_docs], sep='\n\n')
    for idx, split_doc in enumerate(split_docs):
        split_docs[idx].metadata['created_date'] = "1970-01-01"
        print(idx, ":", split_doc.page_content, end="\n\n")
    
    chroma_db = Chroma.from_documents(split_docs, embeddings)
    # print(f"{type(chroma_db.embeddings) = }")
    print()

    query = "파이썬을 어디에서 관리하는가?"
    print(f"/** <{query}>와 유사도가 높은 답은 '->'로 표시 **/")
    _print(chroma_db.similarity_search_with_score(query))
    _print(chroma_db.similarity_search_with_relevance_scores(query))

    
    # 텍스트를 직접 넣어서 Chroma 객체를 생성하는 방식
    texts = ["안녕하세요", "오늘 날씨가 좋네요"]
    chroma_db = Chroma.from_texts(texts, embeddings)
    # print(f"{chroma_db.embeddings = }")
    query = "반갑습니다"
    print(f"/** <{query}>와 유사도가 높은 답은 '->'로 표시 **/")
    _print(chroma_db.similarity_search_with_score(query, k=2))  # Cosine Distance, 0~2 사이의 값, 작을수록 유사도가 높음
    _print(chroma_db.similarity_search_with_relevance_scores(query, k=2))  # Relevance Score, 0~1 사이의 값, 클수록 유사도가 높음


    # TextLoader 사용하여 FAISS 객체를 생성하는 방식
    make_faiss_index(data_path)
    query = "파이썬을 어디에서 관리하는가?"
    faiss_result = faiss_inference(query, k=1)
    print(f"/** <{query}>와 유사도가 가장 높은 답은?? **/")
    print(faiss_result)

    
    # Retriver를 사용하는 방식
    retriever = get_retriever()
    retriever_result = retriever.invoke(query)[0]
    print(retriever_result)


if __name__ == "__main__":
    main()