import os
import json
import vertexai
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part

# Import the BigQuery tool
from .tools.bq_tools import get_customer_context

# 1. Load Environment Variables
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash-001") # Fallback to flash if not set

if not PROJECT_ID:
    raise ValueError("PROJECT_ID environment variable is missing.")

# Initialize Vertex AI context
vertexai.init(project=PROJECT_ID, location=LOCATION)

# 2. Define the Tool for the LLM
get_context_declaration = FunctionDeclaration(
    name="get_customer_context",
    description="Retrieves a customer's RFM features and AI-assigned segment from BigQuery.",
    parameters={
        "type": "object",
        "properties": {
            "customer_id": {"type": "integer", "description": "The unique Customer ID"}
        },
        "required": ["customer_id"]
    }
)

marketing_tools = Tool(function_declarations=[get_context_declaration])

# 3. Define the System Instructions (The Agent Persona)
SYSTEM_INSTRUCTION = """
You are 'CustomerMind AI', an elite Principal MarTech Agent working for an enterprise retailer.
Your goal is to generate highly personalized Next-Best-Action (NBA) marketing strategies.

Rules:
1. ALWAYS use the 'get_customer_context' tool to look up the customer's data before making a recommendation.
2. Analyze their Segment, Income, Recency, and Total Spend to justify your recommendation.
3. If they are a high-value segment but have high recency (churn risk), prioritize retention.
4. If they have low spend but high campaign acceptance, prioritize cross-sell bundles.
5. Keep the output professional, actionable, and structured (Profile Summary -> Strategic Reasoning -> Action).
"""

# 4. Initialize the Gemini Model dynamically
model = GenerativeModel(
    MODEL_NAME,
    tools=[marketing_tools],
    system_instruction=SYSTEM_INSTRUCTION
)

def generate_nba(customer_id: int):
    """The main execution loop for the Agent."""
    print("==================================================")
    print(f"Initializing CustomerMind AI for Customer {customer_id}...")
    print(f"Using Model: {MODEL_NAME}")
    
    chat = model.start_chat()
    prompt = f"Please recommend a Next-Best-Action marketing strategy for Customer {customer_id}."
    
    response = chat.send_message(prompt)
    
    # [THE FIX]: Robust SDK parsing using the candidates array
    if response.candidates and response.candidates[0].function_calls:
        function_call = response.candidates[0].function_calls[0]
        print(f"\n[Agentic Reasoning]: LLM requested tool -> {function_call.name}({function_call.args})")
        
        if function_call.name == "get_customer_context":
            arg_customer_id = int(function_call.args["customer_id"])
            api_response = get_customer_context(arg_customer_id)
            
            print(f"[Tool Execution]: BigQuery data retrieved successfully.")
            
            # Send the data back to the LLM to finish its thought process
            response = chat.send_message(
                Part.from_function_response(
                    name="get_customer_context",
                    response={"content": api_response}
                )
            )
            
    print("\n[Agentic Reasoning]: Strategy generated successfully.")
    return response.text

