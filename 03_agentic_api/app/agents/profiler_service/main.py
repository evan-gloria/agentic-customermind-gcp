from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from vertexai.generative_models import GenerativeModel
import os

app = FastAPI(title="Profiler Agent API")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)
EXPECTED_API_KEY = os.getenv("API_KEY")


class ProfilerRequest(BaseModel):
    customer_id: int
    model_context: dict  # This catches the cluster ID, segment name, and Kaggle features

class PersonaGenerationRequest(BaseModel):
    stats: list

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return api_key

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
    
@app.post("/api/v1/generate-personas")
async def generate_personas(request: PersonaGenerationRequest, api_key: str = Depends(verify_api_key)):
    """Takes raw cluster demographics and uses Gemini to assign Marketing Persona names."""
    try:
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        
        prompt = f"""
        You are an expert Marketing Strategist. I have run a K-Means clustering algorithm on our Australian customer database and found 5 segments. 
        Here are the average demographic and spending statistics for each segment:
        
        {json.dumps(request.stats, indent=2)}
        
        Provide a professional, concise marketing persona name (e.g., "High-Value Tech Professional", "Budget-Conscious Student") for each segment.
        You MUST return ONLY a valid JSON dictionary where the keys are the centroid_id (as strings "1", "2", etc.) and the values are the segment names. 
        """
        
        agent = GenerativeModel(model_name)
        
        # 🚨 THE ARCHITECT'S SECRET: Force Gemini into strict JSON mode 
        # so it doesn't accidentally output conversational text and crash your pipeline!
        generation_config = {"response_mime_type": "application/json"}
        
        response = agent.generate_content(prompt, generation_config=generation_config)
        
        # Parse the JSON string from Gemini into a real Python dictionary
        persona_mapping = json.loads(response.text)
        
        return {"status": "success", "personas": persona_mapping}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini Profiling Error: {str(e)}")