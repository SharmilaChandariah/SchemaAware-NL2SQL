
import faiss
import numpy as np

class VectorStore:

    def __init__(self, dimension=384):
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []

    def add_document(self, embedding, document):
        embedding = np.array([embedding]).astype('float32')
        self.index.add(embedding)
        self.documents.append(document)

    def search(self, embedding, top_k=3):
        embedding = np.array([embedding]).astype('float32')
        _, indices = self.index.search(embedding, top_k)

        return [
            self.documents[i]
            for i in indices[0]
            if i < len(self.documents)
        ]
