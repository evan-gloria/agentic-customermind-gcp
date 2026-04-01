# 🧠 02: Predictive Layer (BigQuery ML)

This directory contains the machine learning pipeline for the Customer Intelligence Platform. 

Rather than extracting data into external Python environments (like Scikit-Learn or Pandas) for modeling, this platform utilizes **BigQuery ML (BQML)** to train and execute models directly where the data lives. This zero-data-movement architecture ensures enterprise-grade security, infinite scalability, and significantly lower compute latency.

---

## 🏗️ Pipeline Execution Order

To generate the AI-ready semantic layer, execute the following SQL scripts in your Google Cloud BigQuery console in this exact order:

### Step 1: Train the Clustering Model
**File:** `01_train_kmeans.sql`

This script trains an unsupervised K-Means clustering model (`num_clusters=4`) on the feature set generated in Layer 01. It uses standard K-Means++ initialization and automatically standardizes the numerical features (Age, Income, Spend, etc.) to prevent high-variance columns from skewing the clusters.

### Step 2: Evaluate & Test Orchestration Logic
**File:** `02_evaluate_clusters.sql`

This is a diagnostic and testing script. It performs two functions:
1. Calls `ML.EVALUATE` to retrieve the Davies-Bouldin Index and Mean Squared Distance of the model.
2. Simulates the deterministic scoring logic used by the Python `Profiler Service`. It tests mapping the raw mathematical `Centroid_ID` outputs into human-readable psychological profiles (e.g., "High-Value Tech Professional", "Young Family / Upsizer") and calculates simulated affinity scores against a target market category.

### Step 3: Materialize the Semantic Layer
**File:** `03_materialize_semantic_layer.sql`

This script finalizes the predictive pipeline by creating the objects that the downstream Agentic AI (Layer 03) will query:
1. **Materialization:** It runs `ML.PREDICT` across the entire customer base and materializes the results into a static table (`customer_segments_materialized`). This prevents the platform from running costly ML inference every time a user loads a dashboard.
2. **The "One Big Table" (OBT):** It creates the final `v_agent_semantic_layer` view. This view joins the raw customer features with their predicted psychological segments. 

---

## 🤖 AI Agent Integration

The final output of this layer—`customermind_ai.v_agent_semantic_layer`—is the **only** database object exposed to the Vertex AI Text-to-SQL Agent. 

By flattening the relational database and the machine learning predictions into a single wide view, we completely eliminate the need for the LLM to hallucinate complex `JOIN` statements, ensuring highly accurate natural language analytics.