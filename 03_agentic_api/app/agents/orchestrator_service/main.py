from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="Campaign Orchestrator API Gateway")

# Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)
EXPECTED_API_KEY = os.getenv("API_KEY")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return api_key

class CampaignRequest(BaseModel):
    customer_id: int

# In production, these would be Environment Variables. 
# For your portfolio, paste your 4 actual Cloud Run URLs here!
SERVICES = {
    "modeler": os.getenv("URL_MODELER", "https://data-modeling-service-xxx.a.run.app/api/v1/predict"),
    "profiler": os.getenv("URL_PROFILER", "https://profiler-service-xxx.a.run.app/api/v1/profile"),
    "strategist": os.getenv("URL_STRATEGIST", "https://strategist-service-xxx.a.run.app/api/v1/strategize"),
    "reviewer": os.getenv("URL_REVIEWER", "https://reviewer-service-xxx.a.run.app/api/v1/review")
}

@app.post("/api/v1/generate-campaign")
async def run_campaign_pipeline(request: CampaignRequest, api_key: str = Depends(verify_api_key)):
    headers = {"Content-Type": "application/json", "X-API-Key": EXPECTED_API_KEY}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # --- STEP 1: Data Modeler ---
            res_model = await client.post(SERVICES["modeler"], json={"customer_id": request.customer_id}, headers=headers)
            res_model.raise_for_status()
            model_data = res_model.json()

            # --- STEP 2: Profiler ---
            res_prof = await client.post(SERVICES["profiler"], json={"customer_id": request.customer_id, "model_context": model_data}, headers=headers)
            res_prof.raise_for_status()
            persona_brief = res_prof.json().get("persona_brief")

            # --- STEP 3: Strategist ---
            res_strat = await client.post(SERVICES["strategist"], json={"persona_brief": persona_brief}, headers=headers)
            res_strat.raise_for_status()
            strategy = res_strat.json().get("strategy")

            # --- STEP 4: Reviewer ---
            res_rev = await client.post(SERVICES["reviewer"], json={"persona_brief": persona_brief, "strategy": strategy}, headers=headers)
            res_rev.raise_for_status()
            audit_results = res_rev.json().get("audit_results")

            # --- FINAL PAYLOAD ASSEMBLY ---
            return {
                "status": "success",
                "pipeline_results": {
                    "customer_id": request.customer_id,
                    "segment_data": model_data,
                    "persona_brief": persona_brief,
                    "executable_strategy": strategy,
                    "audit_results": audit_results
                }
            }

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Microservice Pipeline Failed at {e.request.url}: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Orchestration Error: {str(e)}")