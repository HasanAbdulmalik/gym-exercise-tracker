import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. PAGE CONFIGURATION (Must be first) ---
st.set_page_config(
    page_title="Titan Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ADVANCED CSS INJECTION (The "Tailwind" Look) ---
# We inject raw CSS to overwrite Streamlit's default boring look.
st.markdown("""
    <style>
    /* 1. Main Background - Deep Slate (Tailwind Slate-900) */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* 2. Remove Streamlit Header/Footer junk */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 3. Custom Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1e293b; /* Slate-800 */
        border-right: 1px solid #334155;
    }
    
    /* 4. "Titan Pro" Card Style */
    .titan-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* 5. Metrics Styling */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8; /* Slate-400 */
        font-size: 0.8rem;
    }
    div[data-testid="stMetricValue"] {
        color: #38bdf8; /* Sky-400 */
        font-size: 1.8rem;
    }
    
    /* 6. Button Styling (Neon Green/Emerald Gradient) */
    .stButton>button {
        background: linear-gradient(to right, #10b981, #059669);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.2s;
        width: 100%;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
    }
    
    /* 7. Input Fields */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #334155;
        color: white;
        border-radius: 8px;
        border: 1px solid #475569;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC & DATA (Same Backend, New Frontend) ---

EXERCISES = {
    "Push Ups": 3.8, "Squats": 5.0, "Running (Jog)": 7.0, "Bench Press": 6.0,
    "Pull Ups": 8.0, "Plank": 3.0, "Deadlift": 6.0, "Cycling": 7.5,
    "Jumping Jacks": 8.0, "Lunges": 4.0, "Bicep Curls": 3.5, "Burpees": 8.0,
    "Yoga": 2.5, "Swimming": 6.0, "Sit Ups": 3.8, "Rowing": 7.0, "Boxing": 9.0
}

if 'log' not in st.session_state:
    st.session_state.log = []

def calculate_calories(met, weight, sets, reps):
    duration_min = sets * 2
    if reps > 15: duration_min *= 1.2
    return round((met * 3.5 * weight) / 200 * duration_min, 1)

# --- 4. THE TITAN PRO INTERFACE ---

# HEADER SECTION
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("<h1 style='text-align: center; font-size: 40px;'>⚡</h1>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color: white; margin-bottom: 0px;'>TITAN PRO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; margin-top: -15px;'>Advanced Performance Tracker</p>", unsafe_allow_html=True)

st.markdown("---")

# USER PROFILE SIDEBAR (Clean & Minimal)
with st.sidebar:
    st.markdown("### 👤 PILOT PROFILE")
    name = st.text_input("Name", "User 01")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        weight = st.number_input("Kg", 30.0, 200.0, 70.0)
    with col_s2:
        height = st.number_input("Meters", 1.0, 2.5, 1.75)
    
    bmi = weight / (height ** 2)
    
    # Download Button logic styled cleanly
    if st.session_state.log:
        df = pd.DataFrame(st.session_state.log)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Data", csv, "titan_log.csv", "text/csv")

# DASHBOARD GRID
col_left, col_right = st.columns([1.5, 2.5], gap="large")

# LEFT COLUMN: HEALTH METRICS (Visual Heavy)
with col_left:
    st.markdown('<div class="titan-card">', unsafe_allow_html=True)
    st.markdown("### 🩺 Body Composition")
    
    # Custom BMI Gauge Color Logic
    if bmi < 18.5: gauge_color = "#38bdf8" # Blue
    elif 18.5 <= bmi < 25: gauge_color = "#4ade80" # Green
    elif 25 <= bmi < 30: gauge_color = "#fbbf24" # Orange
    else: gauge_color = "#f87171" # Red
    
    status_text = "Healthy"
    if bmi < 18.5: status_text = "Underweight"
    elif bmi >= 25: status_text = "Overweight"

    # Plotly Gauge with Dark Theme
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = bmi,
        number = {'font': {'color': "white"}},
        gauge = {
            'axis': {'range': [10, 40], 'tickcolor': "white"},
            'bar': {'color': gauge_color},
            'bgcolor': "#1e293b",
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 18.5], 'color': "rgba(56, 189, 248, 0.3)"},
                {'range': [18.5, 25], 'color': "rgba(74, 222, 128, 0.3)"},
                {'range': [25, 40], 'color': "rgba(248, 113, 113, 0.3)"}
            ],
        }
    ))
    fig.update_layout(paper_bgcolor="#1e293b", font={'color': "white"}, height=250, margin=dict(t=30,b=20,l=30,r=30))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"<div style='text-align: center; color: {gauge_color}; font-weight: bold; font-size: 1.2rem;'>{status_text}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) # End Card

# RIGHT COLUMN: WORKOUT CONSOLE
with col_right:
    # 1. INPUT CONSOLE
    st.markdown('<div class="titan-card">', unsafe_allow_html=True)
    st.markdown("### ⚡ Command Center")
    with st.form("titan_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            exercise = st.selectbox("Exercise Module", list(EXERCISES.keys()))
        with c2:
            sets = st.number_input("Sets", 1, 10, 3)
        with c3:
            reps = st.number_input("Reps", 1, 50, 10)
        
        submit = st.form_submit_button("LOG ACTIVITY")
        
        if submit:
            cals = calculate_calories(EXERCISES[exercise], weight, sets, reps)
            st.session_state.log.append({
                "Time": datetime.now().strftime("%H:%M"),
                "Exercise": exercise,
                "Vol": f"{sets}x{reps}",
                "Burn": cals
            })
            st.toast(f"Activity Logged: {exercise} (-{cals} kcal)", icon="🔥")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. STATS OVERVIEW
    if st.session_state.log:
        df = pd.DataFrame(st.session_state.log)
        total_cals = df['Burn'].sum()
        total_sets = sum(int(x.split('x')[0]) for x in df['Vol'])
        
        # Row of Metrics
        m1, m2, m3 = st.columns(3)
        with m1: m1.metric("Total Burn", f"{total_cals} kcal")
        with m2: m2.metric("Total Volume", f"{total_sets} sets")
        with m3: m3.metric("Session Count", len(df))
        
        # 3. HISTORY TABLE
        st.markdown("### 📜 Mission History")
        # Style the dataframe container
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Burn": st.column_config.NumberColumn("Burn (kcal)", format="%.1f 🔥")
            }
        )
