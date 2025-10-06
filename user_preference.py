from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

# Sample preferences
user_preferences = [
    "User likes leather goods such as bags, belts, and wallets.",
    "Prefers products under a strict budget of $100.",
    "Interested in eco-friendly and sustainable fashion.",
    "Dislikes bright neon colors, prefers neutral tones like black, brown, and grey.",
    "Enjoys high-quality footwear, especially leather boots.",
    "Prefers online shopping platforms with quick delivery options.",
    "Looking for gift suggestions for friends in the tech category.",
    "User has shown interest in luxury watches but prefers discounts.",
    "Interested in reading reviews before making a purchase.",
    "Likes to stay updated with the latest fashion trends.",
    "Interested in fitness and wellness products."
]

# Optional splitting (if texts are long)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
chunks = text_splitter.split_text(" ".join(user_preferences))
print(f"✅ Created {len(chunks)} text chunks.")

# Initialize persistent Chroma client
client = chromadb.PersistentClient(path="./chroma_db")

# Create (or get existing) collection
collection = client.get_or_create_collection(name="user_preferences")

# Embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Create embeddings
embeddings = embedder.encode(chunks).tolist()

# Add to Chroma
collection.add(
    documents=chunks,
    embeddings=embeddings,
    ids=[f"pref_{i}" for i in range(len(chunks))]
)

print("✅ User preferences added to ChromaDB!")