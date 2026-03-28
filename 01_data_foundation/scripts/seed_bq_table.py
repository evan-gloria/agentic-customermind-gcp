import time
from google.cloud import bigquery
from google.api_core.exceptions import Conflict

def seed_database():
    print("Initializing BigQuery Seeding Process...")
    PROJECT_ID = "customermind-ai-efg1049"
    DATASET_ID = f"{PROJECT_ID}.customer_data"
    TABLE_ID = f"{DATASET_ID}.profiles"

    client = bigquery.Client(project=PROJECT_ID)

    # 1. Create the Dataset
    dataset = bigquery.Dataset(DATASET_ID)
    dataset.location = "australia-southeast1"
    try:
        client.create_dataset(dataset, exists_ok=True)
        print(f"Dataset {DATASET_ID} is ready.")
    except Exception as e:
        print(f"Dataset creation note: {e}")

    # 2. Create the Table Schema
    schema = [
        bigquery.SchemaField("customer_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("segment", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("annual_income", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("lifetime_value", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("last_purchase_days_ago", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("purchase_history", "STRING", mode="NULLABLE")
    ]
    
    table = bigquery.Table(TABLE_ID, schema=schema)
    try:
        client.create_table(table, exists_ok=True)
        print(f"Table {TABLE_ID} is ready.")
    except Exception as e:
        print(f"Table creation note: {e}")

    # Give GCP a moment to register the new table structure
    time.sleep(3)

    # 3. Insert Diverse Persona Data using DML (Immediate consistency)
    insert_query = f"""
        INSERT INTO `{TABLE_ID}` 
        (customer_id, segment, annual_income, lifetime_value, last_purchase_days_ago, purchase_history)
        VALUES
        (4141, 'High-Value Tech', 145000.0, 9500.0, 12, 'MacBook Pro, Mechanical Keyboard, Smart Home Hub, VR Headset'),
        (5039, 'Budget-Conscious Student', 22000.0, 150.0, 5, 'Discounted Groceries, Instant Noodles, Refurbished Monitor, Used Textbooks'),
        (101, 'Luxury Traveler', 280000.0, 25000.0, 45, 'First-Class Lounge Pass, Noise-Canceling Headphones, Premium Hard-shell Luggage'),
        (202, 'New Parent', 85000.0, 1200.0, 2, 'Baby Monitor, Bulk Diapers, Organic Baby Food, Ergonomic Carrier'),
        (303, 'Fitness Fanatic', 75000.0, 2100.0, 18, 'Whey Protein Powder, Smart Fitness Watch, Running Shoes, Meal Prep Containers')
    """
    
    try:
        print("Injecting customer personas into BigQuery...")
        query_job = client.query(insert_query)
        query_job.result() # Wait for the job to complete
        print("Success! 5 diverse customer profiles have been injected.")
    except Exception as e:
        print(f"Error inserting data: {e}")

if __name__ == "__main__":
    seed_database()