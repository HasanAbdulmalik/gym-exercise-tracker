import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Titan Pro Gym Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DATABASE ENGINE (Local Storage) ---
DB_FILE = "titan_db.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(new_entry):
    data = load_data()
    data.append(new_entry)
    with open(DB_FILE, "w") as f:
        json.dump(data, f)
    return data

# Load history on startup
if 'history' not in st.session_state:
    st.session_state.history = load_data()

if 'connected' not in st.session_state:
    st.session_state.connected = False

# --- 3. TITAN CSS ENGINE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp {
        background-color: #09090b; 
        font-family: 'Inter', sans-serif;
    }
    
    /* HIDE JUNK */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* TITAN CARDS */
    .titan-card {
        background: rgba(24, 24, 27, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    
    /* SUCCESS LOG CARD */
    .log-success-card {
        background: linear-gradient(90deg, #064e3b, #065f46);
        border: 1px solid #10b981;
        color: #ecfdf5;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        animation: fadeIn 0.5s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* CURSOR FIX */
    .stSelectbox div[data-baseweb="select"] { cursor: pointer !important; }
    .stSelectbox div[data-baseweb="select"] * { cursor: pointer !important; }

    /* TYPOGRAPHY */
    h1, h2, h3 { color: white !important; font-weight: 800 !important; }
    p, label, .stMarkdown { color: #a1a1aa !important; }
    
    /* INPUT FIELDS */
    .stTextInput input, .stNumberInput input {
        background-color: #18181b !important;
        color: white !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
    }
    
    /* STATUS BADGES */
    .status-badge {
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        text-align: center;
        margin-top: 15px; 
        margin-bottom: 15px;
    }
    .status-inactive { background-color: #450a0a; color: #f87171; border: 1px solid #7f1d1d; }
    .status-active { background-color: #052e16; color: #4ade80; border: 1px solid #14532d; }

    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        transition: transform 0.1s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
EXERCISES_DB = {
    "Push Ups": {"met": 3.8, "icon": "💪"},
    "Squats": {"met": 5.0, "icon": "🦵"},
    "Running": {"met": 7.0, "icon": "🏃"},
    "Bench Press": {"met": 6.0, "icon": "🏋️‍♂️"},
    "Pull Ups": {"met": 8.0, "icon": "🧗"},
    "Deadlift": {"met": 6.0, "icon": "🔋"},
    "Cycling": {"met": 7.5, "icon": "🚴"},
    "Burpees": {"met": 8.0, "icon": "🔥"},
    "Boxing": {"met": 9.0, "icon": "🥊"},
    "HIIT": {"met": 10.0, "icon": "⚡"},
    "Yoga": {"met": 2.5, "icon": "🧘"},
    "Swimming": {"met": 6.0, "icon": "🏊‍♂️"}
}

def calculate_calories(met, weight, sets, reps):
    duration_min = sets * 2.5
    if reps > 12: duration_min *= 1.2
    return round((met * 3.5 * weight) / 200 * duration_min, 1)

# --- 5. SIDEBAR (ATHLETE PROFILE) ---
with st.sidebar:
    st.markdown("## ⚡ TITAN PRO")
    st.markdown("### Gym Tracker")
    st.markdown("---")
    
    st.markdown("### 👤 Athlete Profile")
    name = st.text_input("Name", value="User")
    
    c1, c2 = st.columns(2)
    with c1:
        weight = st.number_input("Mass (kg)", 30.0, 200.0, 75.0)
    with c2:
        height = st.number_input("Height (m)", 1.0, 2.5, 1.75)
    
    bmi = weight / (height ** 2)
    
    # CONNECT BUTTON logic
    if not st.session_state.connected:
        st.markdown('<div class="status-badge status-inactive">🔴 SYSTEM INACTIVE</div>', unsafe_allow_html=True)
        if st.button("INITIALIZE SYSTEM"):
            st.session_state.connected = True
            st.rerun()
    else:
        st.markdown('<div class="status-badge status-active">🟢 SYSTEM CONNECTED</div>', unsafe_allow_html=True)
        if st.button("DISCONNECT"):
            st.session_state.connected = False
            st.rerun()

# --- 6. MAIN INTERFACE ---

if not st.session_state.connected:
    st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center; height: 60vh; flex-direction: column;'>
            <h1 style='font-size: 3rem; color: #52525b !important;'>SYSTEM LOCKED</h1>
            <p style='font-size: 1.2rem;'>Please initialize your athlete profile in the sidebar.</p>
        </div>
    """, unsafe_allow_html=True)

else:
    # Clean Header
    st.markdown(f"<h1 style='font-size: 2.5rem;'>WELCOME, {name.upper()}</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # TABS SYSTEM
    tab1, tab2 = st.tabs(["🚀 TRACKER", "📈 HISTORY"])

    # --- TAB 1: DAILY TRACKER ---
    with tab1:
        col1, col2 = st.columns([1, 2], gap="large")

        # LEFT COLUMN (Health Status)
        with col1:
            st.markdown('<div class="titan-card">', unsafe_allow_html=True)
            st.markdown("### 🧬 BMI INDEX")
            
            # BMI Logic
            if bmi < 18.5: status, color = "UNDERWEIGHT", "#3b82f6"
            elif 18.5 <= bmi < 25: status, color = "OPTIMAL", "#10b981"
            elif 25 <= bmi < 30: status, color = "OVERWEIGHT", "#f59e0b"
            else: status, color = "CRITICAL", "#ef4444"
            
            # Gauge
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
            fig.update_layout(height=220, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"<p style='text-align: center; color: {color} !important; font-weight: bold;'>{status}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # RIGHT COLUMN (Input & Log)
        with col2:
            st.markdown('<div class="titan-card">', unsafe_allow_html=True)
            st.markdown("### 🚀 LOG ACTIVITY")
            
            with st.form("gym_form", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 1, 1], gap="medium")
                with c1:
                    exercise_name = st.selectbox("Select Module", list(EXERCISES_DB.keys()))
                with c2:
                    sets = st.number_input("Sets", 1, 10, 3)
                with c3:
                    reps = st.number_input("Reps", 1, 50, 10)
                
                # Removed the empty spacer call here
                
                if st.form_submit_button("LOG WORKOUT"):
                    ex_data = EXERCISES_DB[exercise_name]
                    cals = calculate_calories(ex_data['met'], weight, sets, reps)
                    
                    entry = {
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Time": datetime.now().strftime("%H:%M"),
                        "Module": exercise_name,
                        "Sets": sets,
                        "Reps": reps,
                        "Burn": cals
                    }
                    st.session_state.history = save_data(entry)
                    
                    # ADVANCED LOG DISPLAY
                    st.markdown(f"""
                        <div class="log-success-card">
                            <h3 style="margin:0; color: #ecfdf5 !important; font-size: 1.2rem;">
                                {ex_data['icon']} &nbsp; {exercise_name.upper()}
                            </h3>
                            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 10px; font-weight: bold;">
                                <span>🔄 {sets} SETS</span>
                                <span>⚡ {reps} REPS</span>
                                <span style="color: #6ee7b7;">🔥 {cals} KCAL</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 2: HISTORY & GRAPHS ---
    with tab2:
        st.markdown('<div class="titan-card">', unsafe_allow_html=True)
        st.markdown("### 📊 ALL-TIME ANALYTICS")
        
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            
            m1, m2, m3 = st.columns(3)
            total_burn = df['Burn'].sum()
            m1.metric("Total Burn (All Time)", f"{int(total_burn)} kcal")
            m2.metric("Total Sets", int(df['Sets'].sum()))
            m3.metric("Workouts Logged", len(df))
            
            st.markdown("---")
            
            st.markdown("#### 🔥 Calorie Burn Timeline")
            chart_df = df.groupby("Date")['Burn'].sum().reset_index()
            
            fig_hist = px.bar(
                chart_df, x="Date", y="Burn", 
                template="plotly_dark",
                color="Burn",
                color_continuous_scale=["#3b82f6", "#8b5cf6"]
            )
            fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_hist, use_container_width=True)
            
            with st.expander("View Raw Data Log"):
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No historical data found. Log your first workout in the Tracker tab!")
        
        st.markdown('</div>', unsafe_allow_html=True)
