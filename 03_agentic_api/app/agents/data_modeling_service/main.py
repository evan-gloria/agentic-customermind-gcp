from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import bigquery

app = FastAPI(title="Data Modeling Agent API")

class PredictRequest(BaseModel):
    customer_id: int

@app.post("/api/v1/predict")
async def get_customer_segment(request: PredictRequest):
    client = bigquery.Client()
    
    # 1. We use ML.PREDICT to evaluate the specific customer against your 4-cluster model
    # We query the View, so the model gets the exact calculated features it was trained on
    query = f"""
        SELECT 
            centroid_id,
            Age, 
            Income, 
            Total_Spend, 
            Total_Purchases, 
            Total_Campaigns_Accepted,
            Recency
        FROM ML.PREDICT(MODEL `customermind_ai.customer_segments`,
          (SELECT * FROM `customermind_ai.v_customer_features` WHERE CustomerID = {request.customer_id}))
    """
    
    try:
        query_job = client.query(query)
        results = list(query_job.result())
        
        if not results:
            return {
                "customer_id": request.customer_id, 
                "status": "not_found",
                "message": "Customer ID not found in v_customer_features."
            }
            
        row = results[0]
        cluster_id = row.centroid_id
        
        # 2. Map the K-Means Centroid ID to a Marketer-Friendly Persona
        # Note: You can adjust these names based on what your actual clusters represent!
        segment_map = {
            1: "High-Income / High-Spend Champions",
            2: "Younger / Promising Potentials",
            3: "Price-Sensitive / Low-Spend",
            4: "Older / Loyal Steady Spenders"
        }
        
        return {
            "status": "success",
            "customer_id": request.customer_id,
            "cluster_id": cluster_id,
            "segment_name": segment_map.get(cluster_id, "Unclassified Segment"),
            "customer_features": {
                "age": row.Age,
                "income": row.Income,
                "total_spend": row.Total_Spend,
                "total_purchases": row.Total_Purchases,
                "campaigns_accepted": row.Total_Campaigns_Accepted,
                "days_since_last_purchase": row.Recency
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))