import os
from openai import OpenAI
import chromadb
from chromadb.config import Settings
import dotenv

dotenv.load_dotenv()
CHROMA_DIR = os.getenv("CHROMA_DIR", "app/rag/data/index")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def embed_query(query: str) -> list:
    """Generate embeddings for the search query."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.embeddings.create(model=EMBED_MODEL, input=query)
    return resp.data[0].embedding

def search(query: str, k: int = 3):
    """
    Search for relevant policy information.
    
    Args:
        query: The search query
        k: Number of results to return
    """
    print(f"\nSearching for: {query}")
    print("-" * 80)
    
    # Generate query embedding
    query_embedding = embed_query(query)
    
    # Search in Chroma
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection("policies")
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    
    # Print results
    for i in range(len(results["documents"][0])):
        metadata = results["metadatas"][0][i]
        print(f"\nResult {i+1}:")
        print(f"Source: {metadata['source']}")
        if 'section' in metadata:
            print(f"Section: {metadata['section']}")
        print(f"Relevance: {1 - results['distances'][0][i]:.3f}")
        print("\nContent:")
        print("-" * 40)
        print(f"{results['documents'][0][i]}")
        print("-" * 80)

if __name__ == "__main__":
    print("\nPolicy Search Examples:\n")
    
    # Test basic info queries
    search("What is the maternity leave duration?")
    search("How many casual leave days do I get?")
    
    print("\nProcess Queries:\n")
    # Test process-related queries
    search("How do I apply for emergency leave?")
    search("What documents are needed for maternity leave?")
    
    print("\nSpecial Cases:\n")
    # Test special case queries
    search("What happens in case of medical complications during maternity?")
    search("Can I take half-day casual leave?")