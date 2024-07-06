from data_loader import load_data
from src.retrieval import RetrievalModel
from src.reader import ReaderModel
from config import DATA_DIR, READER_MODEL_NAME, EMBEDDING_MODEL_NAME, TOP_K_RETRIEVE, QUERY
import yaml
import os

def main():
    path = os.getcwd()
    
    with open(os.path.join(path, "config.yaml"), "r") as yaml_file:
        cfg = yaml.safe_load(yaml_file)
    
    
    data_dir = cfg["DATA_DIR"] # "/mnt/a/constantly-git"  # 데이터 경로 설정
    documents = load_data(data_dir)

    # Retrieval 모델 초기화 및 인덱스 빌드
    retrieval_model = RetrievalModel(cfg["EMBEDDING_MODEL_NAME"])
    retrieval_model.build_index(documents)

    # Reader 모델 초기화
    reader_model = ReaderModel(cfg["READER_MODEL_NAME"])

    # 예제 질의
    query = cfg["QUERY"]

    # Retrieval 단계
    retrieved_docs = retrieval_model.retrieve(query)
    print(f"Retrieved Documents: {retrieved_docs}")

    # Reader 단계
    for doc in retrieved_docs:
        answer = reader_model.extract_answer(query, doc)
        print(f"Extracted Answer: {answer['answer']} (score: {answer['score']})")

if __name__ == "__main__":
    main()