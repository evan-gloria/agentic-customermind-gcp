from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from vertexai.generative_models import GenerativeModel
import os

app = FastAPI(title="Profiler Agent API")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)
EXPECTED_API_KEY = os.getenv("API_KEY")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return api_key

# We update the request model to accept the payload from Agent 1
class ProfilerRequest(BaseModel):
    customer_id: int
    model_context: dict  # This catches the cluster ID, segment name, and Kaggle features

@app.post("/api/v1/profile")
async def generate_profile(request: ProfilerRequest, api_key: str = Depends(verify_api_key)):
    try:
        # 1. Extract the rich data passed from Agent 1
        segment_name = request.model_context.get("segment_name", "Unknown Segment")
        features = request.model_context.get("customer_features", {})
        
        # 2. Formulate a highly structured context string for the LLM
        context_string = (
            f"Assigned ML Segment: {segment_name}\n"
            f"Age: {features.get('age', 'Unknown')}\n"
            f"Annual Income: ${features.get('income', 'Unknown')}\n"
            f"Total Lifetime Spend: ${features.get('total_spend', 'Unknown')}\n"
            f"Total Number of Purchases: {features.get('total_purchases', 'Unknown')}\n"
            f"Previous Campaigns Accepted: {features.get('campaigns_accepted', 'Unknown')}\n"
            f"Days Since Last Purchase: {features.get('days_since_last_purchase', 'Unknown')}\n"
        )

        # 3. Run the Profiler Agent
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        instruction = (
            "You are an expert Customer Data Profiler. Analyze the provided machine learning segment "
            "and raw customer features to output a concise 'Target Persona Brief'. "
            "Highlight their spending power, historical engagement, and explicitly state what kind "
            "of incentives (e.g., premium tech, budget food, luxury travel, etc.) would motivate them. "
            "Do NOT write a marketing strategy. Only write the psychological and financial profile."
        )
        
        agent = GenerativeModel(model_name, system_instruction=instruction)
        response = agent.generate_content(f"Raw Data Context:\n{context_string}")
        
        return {"status": "success", "persona_brief": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))