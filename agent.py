from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from web_search import web_search_tool
from product_scraper import product_scraper_tool
import os, sys
from product_tool import product_comparison_agent_tool, product_comparison_tool
from memory_manager import add_new_memory, get_all_memories
from review_synthesis_tool import review_synthesis_tool


sys.path.append(os.path.dirname(__file__))

# Initialize LLM (can use OpenAI or any supported LLM)
llm = ChatGoogleGenerativeAI(
    model="gemini-pro-latest",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)
#for m in genai.list_models():
#    print(m.name, " — supports ", m.supported_generation_methods)

# Embedding wrapper
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Connect to ChromaDB
vectorstore = Chroma(
    collection_name="user_preferences",
    embedding_function=embedding_model,
    persist_directory="./chroma_db"
)

print(vectorstore._collection.name)
# Get count of stored items
try:
    count = len(vectorstore.get())
    print(f"Number of stored preference documents: {count}")
except Exception as e:
    print("Could not read from ChromaDB:", e)

    
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Tools
retriever_tool = Tool(
    name="PreferenceRetriever",
    func=lambda query: retriever.get_relevant_documents(query),
    description="Fetches user preferences for personalized shopping."
)

# Load tools
tools = [retriever_tool, web_search_tool, product_scraper_tool, review_synthesis_tool, product_comparison_agent_tool]  # Add more tools as needed

# Initialize Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

def run_rag_agent(query: str, k: int = 3) -> str:
    """Orchestrator that combines RAG retrieval with the existing multi-step agent.

    Steps:
    1. Use the Chroma retriever to fetch top-k documents relevant to `query`.
    2. Create a compact context summary from those documents.
    3. Call the initialized agent with the augmented prompt (context + user query).

    Returns the agent response string. Errors and empty retrievals are handled gracefully.
    """
    try:
        # fetch docs (respect the requested k)
        docs = retriever.get_relevant_documents(query)
    except Exception as e:
        # Retriever failed — fall back to running the agent without context
        print(f"Retriever error: {e}")
        try:
            return agent.run({"input": query})
        except Exception as agent_e:
            return f"Both retriever and agent failed: retriever={e}; agent={agent_e}"

    # Build compact context
    if not docs:
        context = ""  # no retrieved context
    else:
        # Keep each doc short: include source (if available) and first 300 characters
        ctx_items = []
        for d in docs[:k]:
            src = None
            try:
                src = d.metadata.get("source") if isinstance(d.metadata, dict) else None
            except Exception:
                src = None
            snippet = (d.page_content[:300] + "...") if len(d.page_content) > 300 else d.page_content
            if src:
                ctx_items.append(f"Source: {src}\n{snippet}")
            else:
                ctx_items.append(snippet)
        context = "\n\n".join(ctx_items)

    # Compose an augmented prompt for the agent
    if context:
        augmented = (
            "Retrieved context (top documents):\n" + context + "\n\n" +
            "User question:\n" + query + "\n\n" +
            "Please use the retrieved context when helpful, and call tools as needed to complete multi-step actions."
        )
    else:
        augmented = query

    try:
        return agent.run({"input": augmented})
    except Exception as e:
        return f"Agent execution failed: {e}"

if __name__ == "__main__":
    query = "Compare the top three noise-canceling headphones and summarize their user reviews"
    # Use the RAG + multi-step agent executor
    response = run_rag_agent(query)
    print(response)