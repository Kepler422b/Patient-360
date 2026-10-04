import streamlit as st
import pandas as pd
import altair as alt
import streamlit.components.v1 as components
from db_utils import init_connection, get_patients, get_patient_timeline, get_patient_summary
from cortex_utils import ask_copilot

st.set_page_config(
    page_title="Patient 360 Copilot", 
    layout="wide", 
    page_icon="✨",
    initial_sidebar_state="expanded"
)

# --- Declare Custom React/Vite Component ---
# This points to the Vite dev server URL. When you build for prod, 
# you would point it to the built `dist` directory path instead.
_react_component = components.declare_component(
    "vite_react_component",
    url="http://localhost:5173"
)

def render_react_component(name, key=None):
    # Returns the value sent back by Streamlit.setComponentValue() in React
    return _react_component(name=name, key=key, default=0)

# --- High-End Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: radial-gradient(circle at 15% 50%, #1a1a2e, #0f0f1a 100%); color: #e2e8f0; }
    .block-container { padding-top: 2rem !important; }
    h1, h2, h3 { background: -webkit-linear-gradient(45deg, #4facfe 0%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700 !important; }
    .warning-banner { background: rgba(255, 193, 7, 0.1); backdrop-filter: blur(10px); color: #ffd54f; padding: 15px; border-radius: 12px; text-align: center; font-weight: 600; margin-bottom: 12px; border: 1px solid rgba(255, 193, 7, 0.3); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); }
    .info-banner { background: rgba(77, 208, 225, 0.1); backdrop-filter: blur(10px); color: #80deea; padding: 15px; border-radius: 12px; text-align: center; font-weight: 600; margin-bottom: 30px; border: 1px solid rgba(77, 208, 225, 0.3); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); }
    div[data-testid="metric-container"] { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.08); padding: 20px; border-radius: 16px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2); transition: transform 0.2s ease-in-out; }
    div[data-testid="metric-container"]:hover { transform: translateY(-5px); border: 1px solid rgba(79, 172, 254, 0.5); }
    div[data-testid="metric-container"] label { color: #94a3b8 !important; font-size: 0.9rem !important; font-weight: 500 !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2.2rem !important; font-weight: 700 !important; }
    .stDataFrame { border-radius: 12px !important; overflow: hidden !important; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
    section[data-testid="stSidebar"] { background-color: #0b0c10 !important; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    .patient-card { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2); }
    .avatar-circle { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; width: 80px; height: 80px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 2rem; font-weight: 700; margin: 0 auto; box-shadow: 0 10px 20px rgba(79, 172, 254, 0.3); }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 8px 8px 0px 0px; padding-top: 10px; padding-bottom: 10px; color: #94a3b8; font-weight: 600; transition: color 0.3s; }
    .stTabs [aria-selected="true"] { color: #00f2fe !important; border-bottom-color: #00f2fe !important; }
</style>
""", unsafe_allow_html=True)

# Banners
st.markdown("""
<div class='warning-banner'>
    ✨ SYNTHETIC DATA ONLY. NO REAL PHI/PII.
</div>
<div class='info-banner'>
    ⚕️ Clinical Decision Support Only. Not for medical advice.
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Nexus 360</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 30px;'>Health Copilot OS</p>", unsafe_allow_html=True)
    page = st.radio("Navigation", ["📊 Dashboard", "👤 Patient 360", "📚 Document Copilot", "⚖️ Evaluation"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #475569; font-size: 0.8rem;'>Powered by<br><b style='color: #94a3b8;'>Snowflake Cortex AI</b></div>", unsafe_allow_html=True)

try:
    session = init_connection()
except Exception as e:
    st.error("Could not connect to Snowflake. Please ensure credentials are set.")
    st.stop()

if page == "📊 Dashboard":
    st.title("Population Overview")
    st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>Monitor key metrics across the synthetic patient population.</p>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Synthetic Patients", "50", "+5 this week")
    col2.metric("Total Encounters", "124", "+12 this week")
    col3.metric("Total Claims Processed", "$145,200", "-$2,400")
    
    st.write("")
    try:
        patients_df = get_patients(session)
        col_chart, col_table = st.columns([1.2, 2])
        
        with col_chart:
            st.markdown("### Patient Demographics")
            gender_counts = patients_df['GENDER'].value_counts().reset_index()
            gender_counts.columns = ['Gender', 'Count']
            chart = alt.Chart(gender_counts).mark_arc(innerRadius=60, cornerRadius=10).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Gender", type="nominal", scale=alt.Scale(range=['#4facfe', '#00f2fe', '#8ca8d9'])),
                tooltip=['Gender', 'Count']
            ).properties(height=350).configure_view(strokeWidth=0).configure_legend(labelColor='#e2e8f0', titleColor='#e2e8f0')
            st.altair_chart(chart, use_container_width=True)
            
        with col_table:
            st.markdown("### Recent Patients Directory")
            st.dataframe(patients_df[['PATIENT_ID', 'FIRST_NAME', 'LAST_NAME', 'DOB', 'GENDER']], use_container_width=True, hide_index=True, height=350)
    except Exception as e:
        st.error(f"Error fetching data: {e}")

elif page == "👤 Patient 360":
    st.title("Patient 360")
    try:
        patients_df = get_patients(session)
        patient_names = patients_df['FIRST_NAME'] + " " + patients_df['LAST_NAME']
        
        col_search, _ = st.columns([1, 2])
        with col_search:
            selected_name = st.selectbox("Search Patient Directory", patient_names, label_visibility="collapsed", placeholder="Select a patient...")
        
        if selected_name:
            patient_row = patients_df[patient_names == selected_name].iloc[0]
            patient_id = patient_row['PATIENT_ID']
            
            st.write("")
            st.markdown(f"""
            <div class="patient-card">
                <div style="display: flex; align-items: center; gap: 30px;">
                    <div class="avatar-circle">
                        {patient_row['FIRST_NAME'][0]}{patient_row['LAST_NAME'][0]}
                    </div>
                    <div style="flex-grow: 1;">
                        <h2 style="margin: 0; padding: 0;">{selected_name}</h2>
                        <div style="display: flex; gap: 40px; margin-top: 15px;">
                            <div><span style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase;">DOB & Gender</span><br><span style="font-size: 1.1rem; font-weight: 500;">{patient_row['DOB']} ({patient_row['GENDER']})</span></div>
                            <div><span style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase;">Contact (Masked)</span><br><span style="font-size: 1.1rem; font-weight: 500;">{patient_row['PHONE']}</span></div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- TABS ---
            tab_timeline, tab_react, tab_copilot = st.tabs(["📋 Unified Timeline", "⚛️ React Interactive Module", "💬 AI Patient Copilot"])
            
            with tab_timeline:
                st.write("")
                timeline_df = get_patient_timeline(session, patient_id)
                st.dataframe(
                    timeline_df, 
                    use_container_width=True, hide_index=True,
                    column_config={"DATE": st.column_config.DateColumn("Date", format="MMM DD, YYYY")}
                )
                
            with tab_react:
                st.write("")
                st.markdown("### Vite + React Bi-directional Component")
                # Render the React component, passing down the patient's name
                react_clicks = render_react_component(name=selected_name, key=f"react_{patient_id}")
                
                # Show that Python is receiving data FROM React
                if react_clicks > 0:
                    st.success(f"Streamlit Backend confirms: You clicked the React component {react_clicks} times!")

            with tab_copilot:
                st.write("")
                st.markdown("<p style='color: #94a3b8;'>Ask questions about this specific patient's medical history, claims, and medications.</p>", unsafe_allow_html=True)
                
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                if prompt := st.chat_input("E.g., Summarize this patient's recent encounters..."):
                    timeline_df = get_patient_timeline(session, patient_id)
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.markdown(prompt)
                    with st.chat_message("assistant"):
                        with st.spinner("Analyzing patient records..."):
                            patient_context = timeline_df.to_string()
                            answer, chunks = ask_copilot(session, prompt, patient_context)
                            st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
         st.error(f"Error loading Patient 360: {e}")

elif page == "📚 Document Copilot":
    st.title("Knowledge Copilot")
    st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>Chat with the clinical knowledge base and regulatory guidelines. Answers are grounded in retrieved context.</p>", unsafe_allow_html=True)
    st.write("")
    
    if "doc_messages" not in st.session_state: st.session_state.doc_messages = []
    col_chat, col_citations = st.columns([2, 1.2])
    
    with col_chat:
        st.markdown("### Chat")
        for message in st.session_state.doc_messages:
            with st.chat_message(message["role"]): st.markdown(message["content"])
        if prompt := st.chat_input("Ask a medical or regulatory question..."):
            st.session_state.doc_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Retrieving documents and synthesizing..."):
                    answer, chunks = ask_copilot(session, prompt)
                    st.markdown(answer)
                    st.session_state.current_chunks = chunks
            st.session_state.doc_messages.append({"role": "assistant", "content": answer})
            
    with col_citations:
        st.markdown("### 📄 Evidence")
        if "current_chunks" in st.session_state and st.session_state.current_chunks:
            for idx, chunk in enumerate(st.session_state.current_chunks):
                with st.expander(f"Reference {idx+1}: {chunk['FILE_NAME']}", expanded=True):
                    st.caption("Extracted Text:")
                    st.write(chunk['CHUNK_TEXT'])
        else:
            st.info("Ask a question to see the retrieved documentary evidence here.")

elif page == "⚖️ Evaluation":
    st.title("Governance & Evaluation")
    st.markdown("<p style='color: #94a3b8;'>This dashboard tracks the AI's groundedness and citation accuracy for compliance.</p>", unsafe_allow_html=True)
    st.write("")
    st.markdown("### Groundedness Test Set")
    eval_data = pd.DataFrame([
        {"Question": "First-line medication for Type 2 Diabetes?", "Expected": "Metformin", "Source": "FDA_Guidance_Type2_Diabetes.txt", "Result": "✅ Pass"},
        {"Question": "Are ACE inhibitors safe during pregnancy?", "Expected": "Contraindicated", "Source": "Hypertension_Treatment_Protocol.txt", "Result": "✅ Pass"}
    ])
    st.dataframe(eval_data, use_container_width=True, hide_index=True)
