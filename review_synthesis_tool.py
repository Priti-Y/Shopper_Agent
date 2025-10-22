from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate

# Step 1: Define input model
class MultiReviewInput(BaseModel):
    reviews: list[str] = Field(..., description="A list of unstructured review texts to analyze")

# Step 2: Define the system prompt
multi_review_prompt = """
You are an expert review analyst trained to summarize customer feedback.

Your task is to analyze multiple product reviews and extract a combined, structured list of Pros and Cons
that reflect the overall sentiment of the reviewers.

### Instructions
1. Read all reviews carefully.
2. Identify the **most common positive points** (Pros).
3. Identify the **most common negative points** (Cons).
4. Merge similar ideas (e.g., "great sound" and "excellent audio" → "Good sound quality").
5. Ignore neutral or irrelevant comments.
6. Return your response in this **exact JSON format**:

{
  "Pros": [
    "common pro statement 1",
    "common pro statement 2"
  ],
  "Cons": [
    "common con statement 1",
    "common con statement 2"
  ]
}

### Guidelines
- Be concise and specific — one short sentence per point.
- Do not include explanations outside the JSON.
- Keep the number of items balanced (around 3–5 per section).
- If only Pros or only Cons are present, return an empty list for the other.
- Do not invent points not reflected in the reviews.
"""

# Step 3: Define model and prompt chain
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_template(multi_review_prompt)

def synthesize_reviews(reviews: list[str]):
    """
    Combines multiple review texts into a structured list of common Pros and Cons.
    """
    joined_reviews = "\n\n---\n\n".join(reviews)
    response = (prompt | model).invoke({"input": joined_reviews})
    return response.content.strip()




# Step 4: Wrap as LangChain tool
review_synthesis_tool = StructuredTool.from_function(
    func=synthesize_reviews,
    name="review_synthesis_tool",
    description="Extracts aggregated Pros and Cons from multiple product reviews.",
    args_schema=MultiReviewInput,
)