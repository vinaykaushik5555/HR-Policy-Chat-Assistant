import os
import sys
from app.rag.loader import load_policy_files
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import dotenv

dotenv.load_dotenv()
DATA_DIR = os.getenv("POLICY_DATA_DIR", "app/rag/data/sample_policies")
CHROMA_DIR = os.getenv("CHROMA_DIR", "app/rag/data/index")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def embed_texts(texts):
	client = OpenAI(api_key=OPENAI_API_KEY)
	resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
	return [e.embedding for e in resp.data]

def main():
	print(f"Loading policies from {DATA_DIR}")
	print(f"Using embedding model: {EMBED_MODEL}")
	docs = load_policy_files(DATA_DIR)
	texts = [d["text"] for d in docs]
	print(f"Embedding {len(texts)} chunks...")
	embeddings = embed_texts(texts)
	client = chromadb.PersistentClient(path=CHROMA_DIR, settings=Settings(anonymized_telemetry=False))
	collection = client.get_or_create_collection("policies")
	print(f"Upserting into Chroma at {CHROMA_DIR}")
	metadatas = [doc['metadata'] for doc in docs]
	ids = [f"chunk-{i}" for i in range(len(texts))]
	collection.upsert(
		ids=ids,
		embeddings=embeddings,
		documents=texts,
		metadatas=metadatas
	)
	print("Ingestion complete.")

if __name__ == "__main__":
	main()
