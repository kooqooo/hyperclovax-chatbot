""" Author: @kooqooo
Hugging Face API로 테스트 결과,
torch를 사용하여 embedding을 하면 결과가 유사하게 나옴
langchain의 embed_documents함수는 유사하지 않음
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

class LangchainEmbedder:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embedder = HuggingFaceEmbeddings(model_name=self.model_name)
        
    def embed_text(self, text: str):
        return self.embedder.embed_documents([text])

if __name__ == "__main__":
    model_name = "BM-K/KoSimCSE-roberta-multitask"

    # Using the custom TextEmbedder class
    custom_embedder = TextEmbedder(model_name)
    text = "안녕하세요"
    custom_embeddings = custom_embedder.embed_text(text)
    print("Custom Embeddings shape:", custom_embeddings.shape)
    print("Custom Embeddings:", custom_embeddings)
    
    # Using the LangchainEmbedder class
    langchain_embedder = LangchainEmbedder(model_name)
    langchain_embeddings = langchain_embedder.embed_text(text)
    print("Langchain Embeddings:", langchain_embeddings)
