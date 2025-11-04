from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from typing import List
import json

# Step 1: Define input model
class MultiReviewInput(BaseModel):
    # Use typing.List for broader compatibility with pydantic/langchain parsing
    reviews: List[str] = Field(..., description="A list of unstructured review texts to analyze")

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
# ---- Define the synthesis function ----
def synthesize_reviews(reviews: list[str]) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    joined_reviews = "\n".join(reviews)
    prompt = PromptTemplate(
        input_variables=["reviews"],
        template=(
            "Analyze the following product reviews and summarize them into key Pros and Cons:\n\n{reviews}"
        ),
    )
    chain = prompt | llm
    response = chain.invoke({"reviews": joined_reviews})
    return response.content

# ---- Add auto-handling for stringified lists ----
def safe_synthesize_reviews(reviews):
    """Accepts the keyword argument `reviews` (list or string). If a string is provided,
    attempt to JSON-decode it into a list; otherwise treat it as a single review.
    This matches the MultiReviewInput args schema so StructuredTool can call the
    function with the `reviews=` keyword.
    """
    # If passed as stringified list, safely parse it
    if isinstance(reviews, str):
        try:
            parsed = json.loads(reviews)
            # If the parsed value isn't a list, wrap it
            if isinstance(parsed, list):
                reviews = parsed
            else:
                reviews = [str(parsed)]
        except json.JSONDecodeError:
            reviews = [reviews]

    # Ensure we have a list of strings
    if not isinstance(reviews, list):
        reviews = [str(reviews)]

    return synthesize_reviews(reviews)

# ---- Create the Tool ----
review_synthesis_tool = StructuredTool.from_function(
    name="review_synthesis_tool",
    description="Summarize multiple product reviews into clear Pros and Cons.",
    func=safe_synthesize_reviews,
    args_schema=MultiReviewInput,
)