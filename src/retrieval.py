from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RetrievalModel:
    def __init__(self, model):
        self.embedding_model = SentenceTransformer(model)
        self.index = None
        self.documents = []

    def build_index(self, documents):
        self.documents = documents
        embeddings = self.embedding_model.encode(documents, convert_to_tensor=True)
        embeddings = embeddings.cpu().detach().numpy()

        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def retrieve(self, query, top_k=5):
        query_embedding = self.embedding_model.encode([query], convert_to_tensor=True)
        query_embedding = query_embedding.cpu().detach().numpy()

        D, I = self.index.search(query_embedding, top_k)
        results = [self.documents[i] for i in I[0]]
        return results