from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from web_search import web_search_tool
import google.generativeai as genai

from langchain.prompts import PromptTemplate

prompt = PromptTemplate.from_template("""
You are an AI assistant with access to tools.
Always respond with either:
- "Action: <tool_name>"
- "Action Input: <tool input>"
Or "Final Answer: <your answer>"

Question: {input}
""")
# Initialize LLM (can use OpenAI or any supported LLM)
llm = ChatGoogleGenerativeAI(
    model="gemini-pro-latest",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)
#for m in genai.list_models():
#    print(m.name, " — supports ", m.supported_generation_methods)

# Load tools
tools = [web_search_tool]

# Create the agent
agent = initialize_agent(
    tools=tools,    
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"prefix": prompt.template},
    verbose=True,
    handle_parsing_errors=True
)

if __name__ == "__main__":
    response = agent.invoke("Find the latest iPhone 13 Pro reviews")
    print(f"*****************************{response}")