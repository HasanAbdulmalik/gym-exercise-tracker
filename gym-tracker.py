import streamlit as st
import pandas as pd
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

# --- 2. DATABASE ENGINE ---
DB_FILE = "titan_db.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_session(session_items):
    data = load_data()
    data.extend(session_items)
    with open(DB_FILE, "w") as f:
        json.dump(data, f)
    return data

if 'history' not in st.session_state:
    st.session_state.history = load_data()
if 'current_workout' not in st.session_state:
    st.session_state.current_workout = []
if 'connected' not in st.session_state:
    st.session_state.connected = False

# --- 3. ULTRA CSS ENGINE ---
st.markdown("""
    <style>
    /* 1. FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@400;600&display=swap');
    
    /* 2. MAIN BACKGROUND */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1f2937 0%, #030712 60%, #000000 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* 3. HEADERS */
    h1, h2, h3, h4 {
        font-family: 'Rajdhani', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #e5e7eb !important;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
    }
    
    /* --- FIX: SIDEBAR TOGGLE VISIBILITY --- */
    
    /* Make the header transparent but NOT hidden */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Hide the top colored decoration line */
    [data-testid="stDecoration"] {
        display: none;
    }
    
    /* Hide the 'Deploy' button and hamburger menu if you want a cleaner look */
    .stDeployButton {
        display: none;
    }
    
    /* FORCE THE SIDEBAR ARROW TO BE VISIBLE AND STYLED */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        color: #3b82f6 !important; /* Neon Blue */
        background-color: rgba(15, 23, 42, 0.8); /* Dark Blue Bg */
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 4px;
        margin-top: 10px;
        margin-left: 10px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebarCollapsedControl"]:hover {
        background-color: #3b82f6;
        color: white !important;
        box-shadow: 0 0 15px #3b82f6;
        transform: scale(1.1);
    }
    
    /* HIDE FOOTER ONLY */
    footer {visibility: hidden;}
    
    /* 4. TITAN GLASS CARDS */
    .titan-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* 5. EXERCISE STACK ITEM */
    .exercise-card {
        background: linear-gradient(90deg, rgba(20, 20, 25, 0.8), rgba(35, 35, 45, 0.6));
        border-left: 4px solid #3b82f6;
        padding: 16px;
        margin-top: 12px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.05);
        animation: slideIn 0.3s ease-out;
    }
    @keyframes slideIn { from { opacity:0; transform: translateY(10px); } to { opacity:1; transform: translateY(0); } }

    /* 6. INPUT FIELDS */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* 7. BUTTONS */
    .stButton button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(37, 99, 235, 0.6);
    }

    /* 8. FINISH BUTTON */
    .finish-btn button {
        background: linear-gradient(135deg, #059669, #047857) !important;
    }
    .finish-btn button:hover {
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.6) !important;
    }

    /* 9. BMI GRADIENT BAR */
    .bmi-bar-bg {
        width: 100%;
        height: 12px;
        background: #374151;
        border-radius: 6px;
        margin-top: 15px;
        position: relative;
        overflow: hidden;
    }
    .bmi-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #60a5fa, #34d399, #fbbf24, #f87171);
    }
    .bmi-cursor {
        width: 4px;
        height: 20px;
        background: white;
        position: absolute;
        top: -4px;
        box-shadow: 0 0 8px white;
        transition: left 0.5s ease;
    }

    /* 10. STATUS DOT */
    .status-dot {
        height: 10px;
        width: 10px;
        background-color: #4ade80;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7);
        animation: pulse 2s infinite;
        margin-right: 8px;
    }
    .status-dot-off {
        background-color: #ef4444;
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        animation: none;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(74, 222, 128, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GYM DATA ---
EXERCISES_DB = {
    "Barbell Squat": {"met": 6.0, "icon": "🏋️‍♂️"},
    "Bench Press": {"met": 5.0, "icon": "💪"},
    "Deadlift": {"met": 6.0, "icon": "🔋"},
    "Overhead Press": {"met": 5.0, "icon": "🆙"},
    "Barbell Row": {"met": 5.5, "icon": "🚣"},
    "Lat Pulldown": {"met": 4.0, "icon": "🔽"},
    "Dumbbell Lunges": {"met": 5.0, "icon": "🦵"},
    "Leg Press": {"met": 4.5, "icon": "🦵"},
    "Incline Bench": {"met": 5.0, "icon": "📐"},
    "Bicep Curls": {"met": 3.5, "icon": "💪"},
    "Tricep Extensions": {"met": 3.5, "icon": "🦾"},
    "Leg Extensions": {"met": 4.0, "icon": "🦵"},
    "Face Pulls": {"met": 4.0, "icon": "👺"},
}

def calculate_calories(met, weight, sets, reps):
    duration_min = sets * 2.5
    return round((met * 3.5 * weight) / 200 * duration_min, 1)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚡ TITAN PRO")
    st.markdown("<p style='opacity:0.6; font-size:0.8rem; margin-top:-15px;'>TACTICAL PERFORMANCE TRACKER</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 🧬 IDENTITY")
    name = st.text_input("Codename", value="User")
    
    c1, c2 = st.columns(2)
    with c1: weight = st.number_input("Mass (kg)", 30.0, 200.0, 75.0)
    with c2: height = st.number_input("Height (m)", 1.0, 2.5, 1.75)
    
    bmi = weight / (height ** 2)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.connected:
        st.markdown(f"""
            <div style="display:flex; align-items:center; background:rgba(239, 68, 68, 0.1); padding:10px; border-radius:8px; border:1px solid rgba(239, 68, 68, 0.3);">
                <div class="status-dot status-dot-off"></div>
                <span style="color:#f87171; font-weight:bold;">OFFLINE</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("INITIALIZE UPLINK"):
            st.session_state.connected = True
            st.rerun()
    else:
        st.markdown(f"""
            <div style="display:flex; align-items:center; background:rgba(74, 222, 128, 0.1); padding:10px; border-radius:8px; border:1px solid rgba(74, 222, 128, 0.3);">
                <div class="status-dot"></div>
                <span style="color:#4ade80; font-weight:bold;">SYSTEM ONLINE</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("TERMINATE UPLINK"):
            st.session_state.connected = False
            st.rerun()

# --- 6. MAIN INTERFACE ---
if not st.session_state.connected:
    st.markdown("""
    <div style='height: 60vh; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #4b5563;'>
        <h1 style='font-size: 5rem; color: #1f2937 !important; text-shadow:none; opacity:0.5;'>LOCKED</h1>
        <p style="letter-spacing: 3px;">SECURE CONNECTION REQUIRED</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"<h1 style='font-size:3rem; margin-bottom:10px;'>WELCOME, <span style='color:#3b82f6;'>{name.upper()}</span></h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🚀 COMMAND CONSOLE", "📊 DATA ARCHIVE"])

    # --- TAB 1: WORKOUT CONSOLE ---
    with tab1:
        col_left, col_right = st.columns([1, 2], gap="large")

        # LEFT: ADVANCED BMI VISUAL
        with col_left:
            st.markdown('<div class="titan-card">', unsafe_allow_html=True)
            st.markdown("### 🧬 BIO-STATUS")
            
            # BMI Calc
            if bmi < 18.5: status, color = "UNDERWEIGHT", "#60a5fa"
            elif 18.5 <= bmi < 25: status, color = "OPTIMAL", "#34d399"
            elif 25 <= bmi < 30: status, color = "OVERWEIGHT", "#fbbf24"
            else: status, color = "CRITICAL", "#f87171"
            
            st.markdown(f"<h1 style='color: {color} !important; font-size: 4rem; margin:0; line-height:1;'>{bmi:.1f}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: {color} !important; font-weight:bold; letter-spacing: 3px; font-size:0.9rem;'>CONDITION: {status}</p>", unsafe_allow_html=True)

            # Gradient Bar
            pct = max(0, min(100, (bmi - 10) / 30 * 100))
            st.markdown(f"""
            <div class="bmi-bar-bg">
                <div class="bmi-bar-fill"></div>
                <div class="bmi-cursor" style="left: {pct}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #9ca3af; margin-top: 5px; font-family:'Rajdhani';">
                <span>10</span><span>18.5</span><span>25</span><span>30</span><span>40</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # RIGHT: LOGGING SYSTEM
        with col_right:
            st.markdown('<div class="titan-card">', unsafe_allow_html=True)
            st.markdown("### 📝 ACTIVE PROTOCOL")
            
            # Input Form
            with st.form("add_exercise_form", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1: ex_name = st.selectbox("MODULE", list(EXERCISES_DB.keys()))
                with c2: sets = st.number_input("SETS", 1, 10, 3)
                with c3: reps = st.number_input("REPS", 1, 50, 10)
                
                if st.form_submit_button("ADD TO STACK"):
                    cals = calculate_calories(EXERCISES_DB[ex_name]['met'], weight, sets, reps)
                    st.session_state.current_workout.append({
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Time": datetime.now().strftime("%H:%M"),
                        "Module": ex_name,
                        "Sets": sets,
                        "Reps": reps,
                        "Burn": cals,
                        "Icon": EXERCISES_DB[ex_name]['icon']
                    })
                    st.rerun()

            # --- DISPLAY THE STACK (CARDS) ---
            if st.session_state.current_workout:
                st.markdown("---")
                st.markdown("#### ⚡ SESSION QUEUE")
                
                for item in st.session_state.current_workout:
                    st.markdown(f"""
                    <div class="exercise-card">
                        <div style="display:flex; align-items:center; gap:15px;">
                            <span style="font-size: 1.5rem;">{item['Icon']}</span>
                            <div>
                                <div style="font-weight:700; color:white; font-family:'Rajdhani'; font-size:1.1rem; letter-spacing:1px;">{item['Module'].upper()}</div>
                                <div style="font-size:0.8rem; color:#94a3b8;">{item['Sets']} SETS × {item['Reps']} REPS</div>
                            </div>
                        </div>
                        <div style="color: #60a5fa; font-weight:bold; font-family:'Rajdhani'; font-size:1.2rem;">+{item['Burn']} <span style="font-size:0.8rem;">KCAL</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- FINISH BUTTON ---
                col_fin, _ = st.columns([1, 1])
                with col_fin:
                    st.markdown('<div class="finish-btn">', unsafe_allow_html=True)
                    if st.button("✅ COMPLETE PROTOCOL & SAVE"):
                        st.session_state.history = save_session(st.session_state.current_workout)
                        st.session_state.current_workout = []
                        st.success("PROTOCOL SAVED TO ARCHIVE")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("PROTOCOL EMPTY. INITIATE FIRST MODULE.")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 2: ANALYTICS ---
    with tab2:
        st.markdown('<div class="titan-card">', unsafe_allow_html=True)
        st.markdown("### 📊 PERFORMANCE METRICS")
        
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("TOTAL ENERGY EXPENDITURE", f"{int(df['Burn'].sum())} KCAL")
            m2.metric("VOLUME (SETS)", int(df['Sets'].sum()))
            m3.metric("VOLUME (REPS)", int(df['Reps'].sum()))
            
            st.markdown("---")
            
            chart_data = df.groupby("Date")['Burn'].sum().reset_index()
            fig = px.bar(chart_data, x="Date", y="Burn", 
                         title="ENERGY OUTPUT TIMELINE",
                         template="plotly_dark",
                         color="Burn", 
                         color_continuous_scale=["#3b82f6", "#8b5cf6"])
            
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Rajdhani",
                title_font_size=20
            )
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("ACCESS RAW LOGS"):
                st.dataframe(df, use_container_width=True)
                
        else:
            st.info("ARCHIVE EMPTY. NO DATA AVAILABLE.")
        
        st.markdown('</div>', unsafe_allow_html=True)
