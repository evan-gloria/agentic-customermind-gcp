-- Evaluate the K-Means clustering model's performance metrics (Davies-Bouldin Index, Mean Squared Distance)
SELECT
  *
FROM
  ML.EVALUATE(MODEL `customermind_ai.customer_segments`);

-- Simulate the Orchestrator passing the category
DECLARE category STRING DEFAULT 'Tech';

WITH PredictedCustomers AS (
    SELECT 
        CustomerID AS customer_id,
        CAST(age AS FLOAT64) AS age_num,
        CAST(income AS FLOAT64) AS income_num,
        CASE Centroid_ID
            WHEN 1 THEN 'High-Value Tech Professional'
            WHEN 2 THEN 'Conservative Retiree'
            WHEN 3 THEN 'Young Family / Upsizer'
            WHEN 4 THEN 'Small Business Owner'
            ELSE 'General Audience'
        END AS segment_name
    FROM ML.PREDICT(MODEL `customermind_ai.customer_segments`, 
                    (SELECT * FROM `customermind_ai.v_customer_features`))
),

SegmentDemographics AS (
    SELECT 
        segment_name,
        COUNT(customer_id) as cohort_size,
        ROUND(AVG(age_num), 1) as avg_age,
        ROUND(AVG(income_num), 0) as avg_income
    FROM PredictedCustomers
    GROUP BY segment_name
)

SELECT 
    segment_name,
    cohort_size,
    avg_age,
    avg_income,
    CASE 
        WHEN category IN ('Tech', 'Telco') AND segment_name LIKE '%Tech%' THEN 95
        WHEN category IN ('Groceries', 'Home') AND segment_name LIKE '%Family%' THEN 88
        WHEN category IN ('Food', 'Retail') AND segment_name LIKE '%Student%' THEN 92
        WHEN category IN ('Travel', 'Finance') AND segment_name LIKE '%Tech%' THEN 85
        WHEN category IN ('Hardware', 'Groceries') AND segment_name LIKE '%Retiree%' THEN 80
        ELSE 40 + CAST(RAND() * 20 AS INT64) 
    END as affinity_score
FROM SegmentDemographics
ORDER BY affinity_score DESC
LIMIT 3;
