CREATE OR REPLACE MODEL `customermind_ai.customer_segments`
OPTIONS(
  model_type='kmeans',
  num_clusters=4,
  standardize_features=TRUE,
  kmeans_init_method='KMEANS++'
) AS
SELECT 
  Age, 
  Income, 
  Recency, 
  Total_Spend, 
  Total_Purchases,
  Total_Campaigns_Accepted
FROM `customermind_ai.v_customer_features`;