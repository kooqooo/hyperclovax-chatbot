""" Author: @kooqooo
[Hugging Face API로 테스트 결과]
- torch를 사용하여 embedding을 하면 결과가 유사하게 나옴
- langchain의 embed_documents함수는 유사하지 않음

[예상한 원인]
- langchain의 HuggingFaceEmbeddings 클래스는 sentence-transformers를 사용하고 있음
- "BM-K/KoSimCSE-roberta-multitask" 모델은 sentence-transformers에서 지원하지 않음
- "jhgan/ko-sroberta-multitask", "snunlp/KR-SBERT-V40K-klueNLI-augSTS" 모델은 사용 가능

[그 이후의 결과]
- 그럼에도 torch와 langchain의 결과가 다르게 나옴
"""

from transformers import AutoTokenizer, AutoModel
from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings
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
    # model_name = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
    model_name = "jhgan/ko-sroberta-multitask"
    text = "안녕하세요"

    # Using the custom TextEmbedder class
    custom_embedder = TextEmbedder(model_name)
    custom_embeddings = custom_embedder.embed_text(text)
    print("Custom Embeddings shape:", custom_embeddings.shape)
    custom_embeddings = custom_embeddings.flatten().to("cpu")
    print("Custom Embeddings:", custom_embeddings[-5:])
    
    # Using the LangchainEmbedder class
    langchain_embeddings = HuggingFaceEmbeddings(model_name=model_name)
    query_result = langchain_embeddings.embed_query(text)
    print("Langchain Embeddings shape:", len(query_result))
    print("Langchain Embeddings:", query_result[-5:])
