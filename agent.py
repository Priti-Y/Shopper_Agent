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

if __name__ == "__main__":
    query = "Find me a new smart watch under 400$"
    # The output of web_search automatically goes to product_scraper, then to review_synthesis
    response = agent.run({"input": query})
    print(response)