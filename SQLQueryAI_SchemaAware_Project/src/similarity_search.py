
from src.embedding_engine import generate_embedding

def retrieve_context(query, vector_store):
    embedding = generate_embedding(query)
    return vector_store.search(embedding)
