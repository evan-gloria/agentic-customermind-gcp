from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import generate_nba

# Initialize the API
app = FastAPI(
    title="CustomerMind AI API",
    description="Agentic Next-Best-Action REST API for MarTech Integration"
)

# Define the expected incoming JSON payload
class NBARequest(BaseModel):
    customer_id: int

# Create the POST endpoint
@app.post("/api/v1/generate-nba")
async def get_next_best_action(request: NBARequest):
    try:
        # Call the Gemini Agent
        strategy_text = generate_nba(request.customer_id)
        
        # Return the response as structured JSON
        return {
            "status": "success",
            "customer_id": request.customer_id,
            "next_best_action": strategy_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Execution Failed: {str(e)}")

# Health check endpoint for Cloud Run
@app.get("/health")
async def health_check():
    return {"status": "healthy"}