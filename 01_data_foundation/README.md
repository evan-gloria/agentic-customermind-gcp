# 🗄️ 01: Data Foundations

This directory contains the core BigQuery SQL scripts and schema definitions that power the Customer Intelligence Platform. 

There is no application code (Python/FastAPI) in this module. It is strictly the **Data Definition & Engineering Layer**, responsible for bootstrapping the environment, generating enterprise-scale synthetic data, and transforming raw records into analytics-ready features.

---

## 🌱 Prerequisites: The "Seed" Data

Before executing the data pipelines, a small sample of real-world customer data must be loaded into your BigQuery project to act as the "Seed" for our synthetic data generator.

1. Download the [Customer Personality Analysis Dataset](https://www.kaggle.com/datasets/imakash3011/customer-personality-analysis/data) from Kaggle.
2. Open the Google Cloud BigQuery Console.
3. Create a dataset named `customermind_ai`.
4. Use the **"Create Table"** UI to upload the Kaggle CSV. 
5. Name the destination table `raw_customer_profiles` and allow BigQuery to auto-detect the schema.

---

## 🚀 Pipeline Execution Order

This module is designed to be executed sequentially. The scripts are numbered to mimic the behavior of a standard DAG orchestrator (like dbt or Apache Airflow).

### `01_data_preparations.sql` (The 1-Billion-Row Generator)
This script is a heavy-duty ETL process that scales the 2,000-row Kaggle seed data into a massive, production-grade dataset. 

**Architectural Highlights:**
* **Zero-Collision Scaling:** Utilizes BigQuery's `FARM_FINGERPRINT(GENERATE_UUID())` to generate mathematically guaranteed unique `INT64` Customer IDs across a billion rows without hitting single-node CPU bottlenecks.
* **Data Augmentation:** Injects random variance (`RAND()`) into numeric fields (like Income and Recency) to prevent ML model overfitting during the predictive phase.
* **Enterprise Clustering:** The final `raw_customer_profiles_clean` table is explicitly clustered by `ID` to ensure sub-second latency and minimal compute costs when the downstream FastAPI agents perform point-lookups.

### `02_create_feature_view.sql` (The Feature Store)
Once the synthetic data is materialized, this script establishes the semantic view required by the Machine Learning layer.

This view calculates real-time customer metrics (such as aggregated `Total_Spend`, inferred `Age`, and `Total_Campaigns_Accepted`) from the clean profile data.

**Deployment:**
Execute the following SQL directly in your Google Cloud BigQuery console to instantiate the view:

```sql
CREATE OR REPLACE VIEW `customermind_ai.v_customer_features` AS
SELECT 
  ID as CustomerID,
  (2024 - Year_Birth) AS Age,
  Income,
  Recency,
  (MntWines + MntFruits + MntMeatProducts + MntFishProducts + MntSweetProducts + MntGoldProds) AS Total_Spend,
  (NumWebPurchases + NumCatalogPurchases + NumStorePurchases) AS Total_Purchases,
  NumWebVisitsMonth,
  AcceptedCmp1 + AcceptedCmp2 + AcceptedCmp3 + AcceptedCmp4 + AcceptedCmp5 AS Total_Campaigns_Accepted
FROM `customermind_ai.raw_customer_profiles_clean`
WHERE Income IS NOT NULL;
```

---

## ⚠️ Cloud Billing Warning
The `01_data_preparations.sql` script utilizes a `CROSS JOIN` multiplier to generate over **1 Billion rows**. While the compute execution is highly optimized, storing a table of this size will consume active storage quotas in Google Cloud Platform. 

If you are running this as a Proof of Concept (POC), you can lower the `GENERATE_ARRAY` multiplier in the script to generate a smaller dataset (e.g., 10 Million rows) to avoid incurring continuous storage costs.