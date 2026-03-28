-- Evaluate the K-Means clustering model's performance metrics (Davies-Bouldin Index, Mean Squared Distance)
SELECT
  *
FROM
  ML.EVALUATE(MODEL `customermind_ai.customer_segments`);