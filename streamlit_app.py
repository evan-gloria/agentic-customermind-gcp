import streamlit as st
import requests
import time
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Agentic AI Portfolio", page_icon="🧠", layout="wide")

# --- CSS ANIMATION ---
st.markdown("""
<style>
.loading-dots::after {
  content: '.';
  animation: dots 1.5s steps(5, end) infinite;
}
@keyframes dots {
  0%, 20% { color: rgba(0,0,0,0); text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0); }
  40% { color: inherit; text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0); }
  60% { text-shadow: .25em 0 0 inherit, .5em 0 0 rgba(0,0,0,0); }
  80%, 100% { text-shadow: .25em 0 0 inherit, .5em 0 0 inherit; }
}
</style>
""", unsafe_allow_html=True)

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
    st.markdown("### 🛠️ Microservice Architecture")
    st.caption("**UI → API Gateway → Distributed Agents**")
    st.markdown("""
    <div style="font-size: 0.85em; color: #a3a8b8;">
    <b>1. 🟢 Modeler:</b> BigQuery Data Extraction <br>
    <b>2. 🧠 Profiler:</b> Gemini 2.5 Flash Persona <br>
    <b>3. ✍️ Strategist:</b> Gemini 2.5 Flash Campaign <br>
    <b>4. ⚖️ Reviewer:</b> Llama 3.3 Strict Auditing
    </div>
    """, unsafe_allow_html=True)

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
    final_data = {} 
    
    with st.status("🚀 Orchestrator API Gateway Connected...", expanded=True) as status:
        
        # 🌟 NEW: Create a dynamic placeholder block
        ui_placeholder = st.empty()
        tracked_steps = []
        
        try:
            with requests.post(orchestrator_url, json=payload, headers=headers, stream=True) as response:
                
                if response.status_code != 200:
                    st.error(f"Gateway Error {response.status_code}")
                    st.stop()
                    
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        stream_data = json.loads(decoded_line)
                        
                        if stream_data.get("status") == "update":
                            # Add the newest step to our tracker
                            tracked_steps.append(stream_data.get("message"))
                            
                            # Re-render the entire block
                            display_text = ""
                            for i, step in enumerate(tracked_steps):
                                
                                # Split at the first space to safely isolate the text from ANY emoji
                                parts = step.split(" ", 1)
                                clean_text = parts[1] if len(parts) > 1 else step
                                
                                if i == len(tracked_steps) - 1:
                                    # Use the CSS class for the animated dots!
                                    display_text += f"⏳ <i>{clean_text}<span class='loading-dots'></span></i><br><br>" 
                                else:
                                    display_text += f"✅ **{clean_text}**\n\n"
                                    
                            # Overwrite the placeholder with the new UI state
                            ui_placeholder.markdown(display_text, unsafe_allow_html=True)
                            
                        elif stream_data.get("status") == "complete":
                            display_text = ""
                            for step in tracked_steps:
                                parts = step.split(" ", 1)
                                clean_text = parts[1] if len(parts) > 1 else step
                                display_text += f"✅ **{clean_text}**\n\n"
                                
                            ui_placeholder.markdown(display_text, unsafe_allow_html=True)
                            
                            final_data = stream_data.get("pipeline_results", {})
                            status.update(label="✅ Pipeline Execution Complete!", state="complete", expanded=False)
                            
        except Exception as e:
            st.error(f"Connection Error: {e}")
            status.update(label="❌ Connection Failed.", state="error")
            st.stop()

    # --- FINAL DISPLAY ---
    duration = round(time.time() - start_time, 2)
    st.success(f"End-to-end pipeline executed successfully in {duration} seconds.")
    
    # Extracting variables from the final payload
    segment_data = final_data.get("segment_data", {})
    persona_brief = final_data.get("persona_brief", "No brief generated.")
    strategy = final_data.get("executable_strategy", "No strategy generated.")
    audit = final_data.get("audit_results", "No audit results.")

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