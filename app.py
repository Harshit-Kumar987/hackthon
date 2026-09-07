import streamlit as st
import requests

st.set_page_config(
    page_title="Clinical AI Summarizer",
    page_icon="🩺",
    layout="wide"
)

# --- Presets for Quick Testing ---
SAMPLE_CASES = {
    "Select a preset case...": "",
    "Case 1: Chest Pain / Hypertension": (
        "Patient: John Doe, 45, Male. Complaint: Severe chest pain for 3 days. "
        "Severity: Moderate. History: Hypertension. OCR Diagnoses: Angina. "
        "OCR Meds: Tab Aspirin 75mg. OCR Tests: BP: 140/90 mmHg."
    ),
    "Case 2: Respiratory Distress / Asthma": (
        "Patient: Mary Smith, 32, Female. Complaint: High fever and cough for 5 days. "
        "Severity: Severe. History: Asthma. OCR Diagnoses: Acute Bronchitis. "
        "OCR Meds: Syr Amoxicillin 500mg. OCR Tests: SpO2: 95%."
    ),
    "Case 3: Joint Pain / Type 2 Diabetes": (
        "Patient: Alex R, 60, Male. Complaint: Joint stiffness for 2 weeks. "
        "Severity: Mild. History: Diabetes. OCR Diagnoses: Osteoarthritis. "
        "OCR Meds: Tab Paracetamol 500mg. OCR Tests: HbA1c: 7.2%."
    )
}

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Server Configuration")
    api_url = st.text_input(
        "FastAPI / Ngrok Endpoint",
        value="https://delete-chubby-jaunt.ngrok-free.dev/generate_summary",
        help="Paste your active Ngrok or local URL here ending in /generate_summary"
    )
    st.divider()
    st.info(
        "💡 **Tip:** If running locally on the same machine as the API, "
        "use `http://127.0.0.1:8000/generate_summary`."
    )

# --- Main UI ---
st.title("🩺 Clinical Record Summarizer")
st.caption("AI-powered clinical synthesis from raw EHR and OCR records")

selected_preset = st.selectbox("Load sample patient record:", list(SAMPLE_CASES.keys()))

# Update input box if a preset is selected
default_text = SAMPLE_CASES[selected_preset] if selected_preset != "Select a preset case..." else ""

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Input Clinical Record")
    input_text = st.text_area(
        "Raw Patient Notes, Registration & OCR Data:",
        value=default_text,
        height=280,
        placeholder="Enter patient vitals, complaints, history, and OCR data here..."
    )
    
    generate_btn = st.button("Generate Summary", type="primary", use_container_width=True)

with col2:
    st.subheader("AI Doctor Summary")
    
    if generate_btn:
        if not input_text.strip():
            st.warning("Please enter patient data first.")
        elif not api_url.strip():
            st.error("Please provide a valid API endpoint URL in the sidebar.")
        else:
            with st.spinner("Generating summary via Flan-T5 model..."):
                try:
                    payload = {"input_text": input_text.strip()}
                    response = requests.post(api_url.strip(), json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        summary = data.get("ai_summary", "No summary field returned.")
                        
                        st.success("Summary Generated Successfully")
                        st.markdown(
                            f"""
                            <div style="background-color: #f0f2f6; padding: 16px; border-radius: 8px; border-left: 5px solid #0066cc; color: #111;">
                                <pre style="white-space: pre-wrap; font-family: sans-serif; font-size: 15px; margin: 0;">{summary}</pre>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Download button for saving summary
                        st.download_button(
                            label="📥 Download Clinical Summary",
                            data=summary,
                            file_name="clinical_summary.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error(f"API Error ({response.status_code}): {response.text}")
                
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the API server. Check if your Uvicorn/Ngrok server is running and the URL is correct.")
                except requests.exceptions.Timeout:
                    st.error("Request timed out. The model took too long to generate a response.")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
    else:
        st.info("Input clinical notes on the left and click **Generate Summary**.")
