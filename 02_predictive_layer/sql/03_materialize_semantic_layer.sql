CREATE OR REPLACE TABLE `customermind_ai.customer_segments_materialized` AS
SELECT 
        CustomerID AS customer_id,
        CAST(age AS FLOAT64) AS age_num,
        CAST(income AS FLOAT64) AS income_num,
        -- This case statement is for reference. This segment will be dynamic every time we refresh the model
        CASE Centroid_ID
            WHEN 1 THEN 'High-Value Tech Professional'
            WHEN 2 THEN 'Conservative Retiree'
            WHEN 3 THEN 'Young Family / Upsizer'
            WHEN 4 THEN 'Small Business Owner'
            WHEN 5 THEN 'Student / Deal Hunter'
            ELSE 'General Audience'
        END AS segment_name
FROM 
  ML.PREDICT(
    MODEL `customermind_ai.customer_segments`, -- Change to your actual model name!
    TABLE `customermind_ai.v_customer_features`
  );

CREATE OR REPLACE VIEW `customermind_ai.v_agent_semantic_layer` AS
SELECT 
    f.CustomerID,
    f.Age,
    f.Income,
    f.NumWebVisitsMonth,
    f.Total_Spend,
    f.Total_Purchases,
    s.segment_name
FROM 
    `customermind_ai.v_customer_features` f
LEFT JOIN 
    `customermind_ai.customer_segments_materialized` s 
ON 
    f.CustomerID = s.customer_id;