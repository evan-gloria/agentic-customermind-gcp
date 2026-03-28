from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import feedparser
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part
import os

app = FastAPI(title="Strategist Agent API")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)
EXPECTED_API_KEY = os.getenv("API_KEY")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return api_key

class StrategistRequest(BaseModel):
    persona_brief: str

# 1. Define the Tool
def fetch_ozbargain_deals() -> str:
    feed = feedparser.parse("https://www.ozbargain.com.au/feed")
    deals = [f"- {entry.title}\n  Link: {entry.link}" for entry in feed.entries[:15]]
    return "\n".join(deals) if deals else "No live deals found."

oz_func = FunctionDeclaration(
    name="fetch_ozbargain_deals",
    description="Retrieves active deals trending on OzBargain Australia.",
    parameters={"type": "object", "properties": {}}
)
deal_hunter_tool = Tool(function_declarations=[oz_func])

@app.post("/api/v1/strategize")
async def generate_strategy(request: StrategistRequest, api_key: str = Depends(verify_api_key)):
    try:
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        instruction = (
            "You are a Campaign Strategist. Read the provided 'Target Persona Brief'. "
            "You MUST use the `fetch_ozbargain_deals` tool to find 1-2 real-world deals matching the brief. "
            "Write the final Next-Best-Action marketing strategy incorporating those deals."
        )
        agent = GenerativeModel(model_name, tools=[deal_hunter_tool], system_instruction=instruction)
        
        chat = agent.start_chat()
        response = chat.send_message(f"Target Persona Brief:\n\n{request.persona_brief}")
        
        # THE FIX: Check the first candidate for function calls
        if response.candidates and response.candidates[0].function_calls:
            for call in response.candidates[0].function_calls:
                if call.name == "fetch_ozbargain_deals":
                    deals_text = fetch_ozbargain_deals()
                    response = chat.send_message(
                        Part.from_function_response(name="fetch_ozbargain_deals", response={"content": deals_text})
                    )
                    
        return {"status": "success", "strategy": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))