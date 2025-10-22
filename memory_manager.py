
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
import uuid
from langchain_core.tools import tool


# Initialize embedding model
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Connect to existing ChromaDB collection
vectorstore = Chroma(
    collection_name="user_preferences",
    embedding_function=embedding_model,
    persist_directory="./chroma_db"
)

@tool
def add_new_memory(text: str):
    """
    Adds a new user preference or feedback to the existing ChromaDB memory.
    """
    if not text.strip():
        print("Empty input, nothing to add.")
        return
    
    memory_id = f"mem_{uuid.uuid4().hex[:8]}"
    vectorstore.add_texts(
        texts=[text],
        ids=[memory_id]
    )
    vectorstore.persist()
    print(f"Added new memory: '{text}' (ID: {memory_id})")


def get_all_memories():
    """
    Returns all stored memories for debugging or verification.
    """
    results = vectorstore._collection.get()
    return results['documents']
