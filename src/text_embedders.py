""" Author: @kooqooo
[Hugging Face API로 테스트 결과]
- torch를 사용하여 embedding을 하면 결과가 유사하게 나옴
- langchain의 embed_documents함수는 유사하지 않음

[예상한 원인]
- langchain의 HuggingFaceEmbeddings 클래스는 sentence-transformers를 사용하고 있음
- "BM-K/KoSimCSE-roberta-multitask" 모델은 sentence-transformers에서 지원하지 않음
- "jhgan/ko-sroberta-multitask", "snunlp/KR-SBERT-V40K-klueNLI-augSTS" 모델은 사용 가능

[새로 확인한 사항]
1. sentence-transformers를 지원하지 않는 모델은 torch를 사용하는 것과 허깅페이스 API를 사용하는 것이 유사한 결과를 보임
2. sentence-transformers를 지원하는 모델은 langchain과 허깅페이스 API와 유사한 결과를 보임
3. sentence-transformers 지원하는 모델에 한하여 langchain의 HuggingFaceEmbeddings 클래스 사용 가능
"""
import os

from transformers import AutoTokenizer, AutoModel
from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings.huggingface import HuggingFaceInferenceAPIEmbeddings
from sentence_transformers import SentenceTransformer
import torch

class TextEmbedder:
    def __init__(self, model_name: str):
        """
        Initialize the TextEmbedder with a specified model from Hugging Face.
        
        Parameters:
        model_name (str): The name of the Hugging Face model to use for generating embeddings.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        
    def embed_text(self, text: str) -> torch.Tensor:
        """
        Generate embeddings for a given text.
        
        Parameters:
        text (str): The input text to embed.
        
        Returns:
        torch.Tensor: The embeddings of the input text.
        """
        inputs = self.tokenizer(text, return_tensors='pt').to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state[:, 0, :]  # Return the embedding for the [CLS] token


if __name__ == "__main__":
    # model_name = "BM-K/KoSimCSE-roberta-multitask" # Not supported by sentence-transformers
    # model_name = "snunlp/KR-SBERT-V40K-klueNLI-augSTS" # Supported by sentence-transformers
    model_name = "jhgan/ko-sroberta-multitask"  # Supported by sentence-transformers
    text = "안녕하세요"

    # Using the custom TextEmbedder class
    custom_embedder = TextEmbedder(model_name)
    custom_embeddings = custom_embedder.embed_text(text)
    print("Custom Embeddings shape:", custom_embeddings.shape)
    custom_embeddings = custom_embeddings.flatten().to("cpu")
    print("Custom Embeddings:", custom_embeddings[:5])
    
    # Using the LangchainEmbedder class
    langchain_embeddings = HuggingFaceEmbeddings(model_name=model_name)
    query_result = langchain_embeddings.embed_query(text)
    print("Langchain Embeddings shape:", len(query_result))
    print("Langchain Embeddings:", query_result[:5])
    
    # Using the LangchainInferenceAPIEmbedder class
    inference_api_key = os.getenv("HF_API_KEY", "YOUR_API_KEY")
    inference_api_embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=inference_api_key, model_name=model_name)
    api_query_result = inference_api_embeddings.embed_query(text)
    print("Inference API Embeddings shape:", len(api_query_result))
    print("Inference API Embeddings:", api_query_result[:5])

    # Using sentence-transformers
    model = SentenceTransformer(model_name)                     # 모델 로드
    embeddings = model.encode([text], convert_to_tensor=True)   # 문장 임베딩 생성
    print("Sentence-Transformers Embeddings shape:", embeddings.shape)
    print("Sentence-Transformers Embeddings:", embeddings[0][:5])