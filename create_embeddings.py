from sentence_transformers import SentenceTransformer
sentences = "This is an example sentence"

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# embeddings = model.encode(sentences)
# print(embeddings)
def create_embeddings(sentence:str):
    embeddings = model.encode(sentences=sentence)
    return embeddings