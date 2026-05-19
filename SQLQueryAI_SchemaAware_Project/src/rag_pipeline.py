
from src.embedding_engine import generate_embedding
from src.vector_store import VectorStore

store = VectorStore()

def index_examples(examples):
    for example in examples:
        embedding = generate_embedding(example)
        store.add_document(embedding, example)

def retrieve_examples(query):
    embedding = generate_embedding(query)
    return store.search(embedding)
