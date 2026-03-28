from google.cloud import bigquery
import json

# Initialize the BigQuery Client. 
# Because we are running in Cloud Shell/GCP, it automatically inherits your credentials and Project ID.
bq_client = bigquery.Client()

def get_customer_context(customer_id: int) -> str:
    """
    Retrieves a customer's RFM features and their AI-assigned segment from BigQuery.
    This function will be provided to Gemini as a tool.
    """
    
    # We use ML.PREDICT to dynamically assign the customer to a cluster on the fly
    query = """
    SELECT 
      centroid_id as Segment,
      Age,
      Income,
      Recency as Days_Since_Last_Purchase,
      Total_Spend,
      Total_Purchases,
      Total_Campaigns_Accepted
    FROM ML.PREDICT(MODEL `customermind_ai.customer_segments`, 
      (SELECT * FROM `customermind_ai.v_customer_features` WHERE CustomerID = @customer_id)
    )
    """
    
    # Parameterized query to prevent SQL injection
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "INT64", customer_id)
        ]
    )
    
    try:
        query_job = bq_client.query(query, job_config=job_config)
        results = query_job.result()
        
        row = next(results, None)
        if row is None:
            return json.dumps({"error": f"Customer {customer_id} not found."})
            
        # Convert the row to a dictionary
        customer_data = dict(row.items())
        return json.dumps(customer_data)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

# Simple test block (only runs if you execute this file directly)
if __name__ == "__main__":
    # Let's test with a known Customer ID from the Kaggle dataset
    test_id = 5524 
    print(f"Testing BQ Tool for Customer {test_id}...")
    print(get_customer_context(test_id))