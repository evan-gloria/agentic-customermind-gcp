import streamlit as st
import requests
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Agentic AI Portfolio", page_icon="🧠", layout="wide")

# --- HEADER ---
st.title("🧠 Enterprise Multi-Agent Orchestration")
st.markdown("**Distributed Microservices Architecture** | *API Gateway Pattern*")
st.divider()

# --- SIDEBAR (Configuration) ---
with st.sidebar:
    st.header("⚙️ System Configuration")
    st.info("Point this UI to your central Orchestrator API Gateway.")
    
    # The single endpoint for the backend
    orchestrator_url = st.text_input(
        "Orchestrator URL", 
        value="http://127.0.0.1:8000/api/v1/generate-campaign",
        help="Paste your Cloud Run Orchestrator URL here for production testing."
    )
    
    st.divider()
    # SECURITY: No hardcoded password! You must type it in.
    api_key = st.text_input("Master API Key", type="password", help="Enter the secure API key to authenticate.")
    
    st.markdown("---")
    st.markdown("### 🛠️ Architecture Diagram")
    st.caption("UI → API Gateway → [Modeler, Profiler, Strategist, Reviewer]")

# --- MAIN INTERFACE ---
st.markdown("### 🏁 Execute Campaign Pipeline")
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    customer_id = st.number_input("Enter Customer ID", min_value=1, value=4141, step=1)
with col2:
    st.write("") 
    st.write("") 
    execute_btn = st.button("Run AI Factory 🚀", type="primary", use_container_width=True)

# --- EXECUTION LOGIC ---
if execute_btn:
    if not api_key:
        st.error("⚠️ Please enter your Master API Key in the sidebar to authenticate.")
        st.stop()

    headers = {"Content-Type": "application/json", "X-API-Key": api_key}
    payload = {"customer_id": int(customer_id)}
    
    start_time = time.time()
    
    # We only need one status spinner now, because the backend handles the sequence!
    with st.status("🚀 Calling API Gateway and running AI pipeline...", expanded=True) as status:
        st.write("Delegating orchestration to the backend microservices...")
        try:
            # The single, asynchronous-backed API call
            response = requests.post(orchestrator_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json().get("pipeline_results", {})
                status.update(label="✅ Pipeline Execution Complete!", state="complete", expanded=False)
            else:
                st.error(f"Gateway Error {response.status_code}: {response.text}")
                st.stop()
        except Exception as e:
            st.error(f"Connection Error: {e}")
            st.stop()

    # --- FINAL DISPLAY ---
    duration = round(time.time() - start_time, 2)
    st.success(f"End-to-end pipeline executed successfully in {duration} seconds.")
    
    # Extracting variables from the nested Orchestrator payload
    segment_data = data.get("segment_data", {})
    persona_brief = data.get("persona_brief", "No brief generated.")
    strategy = data.get("executable_strategy", "No strategy generated.")
    audit = data.get("audit_results", "No audit results.")

    # Layout for results
    st.markdown(f"### 📊 Customer Insights: {segment_data.get('segment_name', 'Unknown Segment')}")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.subheader("🕵️ Persona Brief")
        st.info(persona_brief)
        
        st.subheader("⚖️ Reviewer Audit Result")
        st.warning(audit)
        
    with res_col2:
        st.subheader("🎯 Final Executable Strategy")
        st.markdown(strategy)