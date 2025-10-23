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
#    # Test query
#         query = "Suggest a good handbag"

#         # Example: Add a new memory based on user feedback
#         add_new_memory("User prefers brown leather goods for wallets and belts.")

#         # Optional: print all stored memories to verify
#         print("\n📦 Current stored preferences:")
#         for mem in get_all_memories():
#             print("-", mem)


#         response = agent.invoke(query)
#         print("\n💡 Final Personalized Response:")
#         print(response)
        #   urls = ["https://example.com/product1", "https://example.com/product2"]
        #   print(product_scraper_tool({"url_list": urls}))
    
            # reviews = [
            #     "The battery life is great but it takes long to charge.",
            #     "Excellent performance, but heating issue sometimes.",
            #     "Display is crisp, battery drains fast.",
            # ]

            # # The StructuredTool expects a dict matching the args_schema (MultiReviewInput),
            # # not a bare list. Pass a dict with the key 'reviews' or a Pydantic model instance.
            # # Incorrect: review_synthesis_tool(reviews)  -> raises ValidationError
            # # Correct (direct tool call):
            # # tool_response = review_synthesis_tool({"reviews": reviews})
            # # print("Tool response:\n", tool_response)

            # # If you prefer to invoke the agent (it will route to the tool), use the agent.invoke
            # # call with the agent's expected input format. Example (kept commented):
            # response = agent.invoke({"input": {"reviews": reviews}})
            # print(response)

            example_product = product_comparison_tool(
                product_name="iPhone 13 Pro",
                price=999.99,
                battery_life="Up to 22 hours talk time",
                pros_summary=["Excellent camera", "Smooth ProMotion display", "Strong performance"],
                cons_summary=["Expensive", "No major design changes"]
            )

            # Use Pydantic v2 method
            print(example_product.model_dump_json(indent=2))