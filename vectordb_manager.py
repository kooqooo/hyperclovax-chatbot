from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings


def faiss_inference(query):
    """
    faiss를 이용해 JD 키워드 한줄한줄 받아와서 유사한 기술면접 질문 4개씩을 불러옵니다.
    output으로는 (4 * 키워드 줄 개수 - 중복된 문장)개의 질문이 반환됩니다
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask", model_kwargs={"device": "cuda"}
    )
    store_name = "./FAISS_INDEX_TAG"
    new_db = FAISS.load_local(
        store_name, embeddings, allow_dangerous_deserialization=True
    )
    results = query.split("\n")
    final_result = []
    for i in results:
        docs = new_db.similarity_search(i, k=4)
        page_contents = [final_result.append(doc.page_content) for doc in docs]
    # 중복된 문장 제거
    final_result = list(set(final_result))
    return final_result


def main():
    from text_splitters import character_splitter

    model_name = "jhgan/ko-sroberta-multitask"
    hf_embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # # TextLoader의 load_and_split 메소드를 사용하는 방식
    # split_docs = TextLoader("./wiki.txt").load_and_split(character_splitter)
    # chroma_db = Chroma.from_documents(split_docs, hf_embeddings)

    # # Print the split documents
    # # print(*[split_doc.page_content for split_doc in split_docs], sep='\n\n')
    # for idx, split_doc in enumerate(split_docs):
    #     print(idx, ":", split_doc.page_content, end="\n\n")

    # 텍스를 직접 넣어서 Chroma 객체를 생성하는 방식
    texts = ["안녕하세요", "오늘 날씨가 좋네요"]
    chroma_db = Chroma.from_texts(texts, hf_embeddings)
    print(f"{chroma_db.embeddings = }")
    print()
    print(
        f"{chroma_db.similarity_search_with_score('반갑습니다', k=2) = }"
    )  # Cosine Distance, 작을수록 유사도가 높음
    print()
    print(
        f"{chroma_db.similarity_search_with_relevance_scores('반갑습니다', k=2) = }"
    )  # Relevance Score, 0~1 사이의 값이 나와야하는데 음수가나옴
    print(
        f"{chroma_db.similarity_search_with_relevance_scores('반갑습니다', k=2, score_threshold=0.7) = }"
    )  # 따라서 이 threshold를 만족하는 결과가 없음


if __name__ == "__main__":
    main()
