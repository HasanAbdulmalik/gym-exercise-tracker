import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Titan Ultimate",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE "TITAN" THEME ENGINE (CSS) ---
# This injects high-end CSS to force Streamlit to look like a modern Web App
st.markdown("""
    <style>
    /* IMPORT FONT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* GLOBAL RESET */
    .stApp {
        background-color: #09090b; /* Zinc 950 */
        font-family: 'Inter', sans-serif;
    }
    
    /* HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* TITAN CARDS (Glassmorphism) */
    .titan-card {
        background: rgba(24, 24, 27, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .titan-card:hover {
        border-color: rgba(139, 92, 246, 0.5); /* Purple Glow */
        transform: translateY(-2px);
    }
    
    /* TYPOGRAPHY */
    h1, h2, h3 {
        color: white !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    p, label, .stMarkdown {
        color: #a1a1aa !important; /* Zinc 400 */
    }
    
    /* METRIC VALUE STYLING */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* CUSTOM BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
        transform: scale(1.02);
    }
    
    /* INPUT FIELDS */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #18181b;
        color: white;
        border: 1px solid #27272a;
        border-radius: 10px;
        height: 45px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PYTHON BACKEND LOGIC ---

EXERCISES = {
    "Push Ups": 3.8, "Squats": 5.0, "Running": 7.0, "Bench Press": 6.0,
    "Pull Ups": 8.0, "Deadlift": 6.0, "Cycling": 7.5, "Burpees": 8.0,
    "Boxing": 9.0, "HIIT": 10.0, "Yoga": 2.5, "Swimming": 6.0
}

# Initialize Database (Session State)
if 'log' not in st.session_state:
    st.session_state.log = []

def calculate_calories(met, weight, sets, reps):
    # Logic: More reps = longer time. Heavier weight = more burn.
    duration_min = sets * 2.5 # Avg 2.5 mins per set
    if reps > 12: duration_min *= 1.2
    
    calories = (met * 3.5 * weight) / 200 * duration_min
    return round(calories, 1)

# --- 4. SIDEBAR DASHBOARD ---
with st.sidebar:
    st.markdown("## ⚡ TITAN ULTIMATE")
    st.markdown("---")
    
    # Profile Section
    st.markdown("### 👤 Pilot Profile")
    name = st.text_input("Codename", "Titan-01")
    weight = st.number_input("Mass (kg)", 40.0, 150.0, 75.0)
    height = st.number_input("Height (m)", 1.2, 2.3, 1.80)
    
    # Real-time BMI Calculation
    bmi = weight / (height ** 2)
    
    st.markdown("---")
    # Data Export
    if st.session_state.log:
        df = pd.DataFrame(st.session_state.log)
        st.download_button(
            "💾 Download Mission Log",
            df.to_csv(index=False).encode('utf-8'),
            "titan_mission_log.csv",
            "text/csv"
        )

# --- 5. MAIN INTERFACE ---

# HEADER
st.markdown(f"""
    <div style="text-align: left; padding: 20px 0;">
        <h1 style="font-size: 3rem; margin:0;">WELCOME, {name.upper()}</h1>
        <p style="font-size: 1.2rem; opacity: 0.7;">System Online. Tracking active.</p>
    </div>
""", unsafe_allow_html=True)

# GRID SYSTEM
col1, col2 = st.columns([1, 2], gap="large")

# --- LEFT COLUMN: BIO-METRICS ---
with col1:
    st.markdown('<div class="titan-card">', unsafe_allow_html=True)
    st.markdown("### 🧬 BIO-STATUS")
    
    # BMI Logic
    if bmi < 18.5: status, color = "UNDERWEIGHT", "#3b82f6" # Blue
    elif 18.5 <= bmi < 25: status, color = "OPTIMAL", "#10b981" # Green
    elif 25 <= bmi < 30: status, color = "OVERWEIGHT", "#f59e0b" # Orange
    else: status, color = "CRITICAL", "#ef4444" # Red
    
    # Plotly Gauge Chart (Minimalist Dark Mode)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = bmi,
        number = {'font': {'color': 'white', 'size': 40}},
        gauge = {
            'axis': {'range': [10, 40], 'tickcolor': "#52525b"},
            'bar': {'color': color},
            'bgcolor': "#27272a",
            'bordercolor': "#27272a",
        }
    ))
    fig.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
        <div style="text-align: center; margin-top: -20px;">
            <p style="color: {color} !important; font-weight: bold; letter-spacing: 2px;">{status}</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # QUICK STATS CARD
    if st.session_state.log:
        total_burn = sum(x['Burn'] for x in st.session_state.log)
        st.markdown(f"""
            <div class="titan-card">
                <h3>🔥 TOTAL BURN</h3>
                <div class="metric-value">{int(total_burn)} kcal</div>
                <p>Session Aggregate</p>
            </div>
        """, unsafe_allow_html=True)

# --- RIGHT COLUMN: MISSION CONTROL ---
with col2:
    # 1. INPUT FORM
    st.markdown('<div class="titan-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 LOG ACTIVITY")
    
    with st.form("titan_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            exercise = st.selectbox("Select Module", list(EXERCISES.keys()))
        with c2:
            sets = st.number_input("Sets", 1, 10, 3)
        with c3:
            reps = st.number_input("Reps", 1, 50, 10)
        
        # Spacer
        st.write("") 
        
        if st.form_submit_button("INITIALIZE SEQUENCE"):
            # Backend Calculation
            cals = calculate_calories(EXERCISES[exercise], weight, sets, reps)
            st.session_state.log.append({
                "Timestamp": datetime.now().strftime("%H:%M"),
                "Module": exercise,
                "Volume": f"{sets} x {reps}",
                "Burn": cals
            })
            st.success(f"SEQUENCE COMPLETE: {exercise} logged. (-{cals} kcal)")
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. ANALYTICS & HISTORY
    if st.session_state.log:
        st.markdown('<div class="titan-card">', unsafe_allow_html=True)
        st.markdown("### 📊 MISSION LOG")
        
        df = pd.DataFrame(st.session_state.log)
        
        # Simple Line Chart for Progress
        chart_data = df.reset_index()
        fig_line = px.area(chart_data, x="Timestamp", y="Burn", template="plotly_dark")
        fig_line.update_traces(line_color='#8b5cf6', fillcolor="rgba(139, 92, 246, 0.2)")
        fig_line.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Clean Table
        st.dataframe(
            df, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "Burn": st.column_config.NumberColumn("Energy (kcal)", format="%.1f ⚡")
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
