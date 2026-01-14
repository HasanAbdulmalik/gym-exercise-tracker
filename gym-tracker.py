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
    """Saves a list of exercises as a batch."""
    data = load_data()
    # Add all items from current session
    data.extend(session_items)
    with open(DB_FILE, "w") as f:
        json.dump(data, f)
    return data

# --- 3. STATE MANAGEMENT ---
# Long-term history
if 'history' not in st.session_state:
    st.session_state.history = load_data()

# Temporary "Cart" for the current workout
if 'current_workout' not in st.session_state:
    st.session_state.current_workout = []

if 'connected' not in st.session_state:
    st.session_state.connected = False

# --- 4. ADVANCED CSS & FONTS ---
st.markdown("""
    <style>
    /* IMPORT FUTURISTIC FONT */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    .stApp {
        background-color: #050505; /* Deep Black */
        font-family: 'Inter', sans-serif;
    }
    
    /* HEADERS USE RAJDHANI FONT */
    h1, h2, h3 {
        font-family: 'Rajdhani', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: white !important;
    }

    /* HIDE STREAMLIT UI */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* TITAN GLASS CARDS */
    .titan-card {
        background: rgba(20, 20, 20, 0.8);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }
    
    /* EXERCISE ITEM CARD (The "Stack") */
    .exercise-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(90deg, #1e1e24, #2a2a35);
        border-left: 4px solid #3b82f6;
        padding: 15px 20px;
        margin-top: 10px;
        border-radius: 8px;
        animation: slideIn 0.3s ease-out;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* BMI BAR CONTAINER */
    .bmi-container {
        position: relative;
        height: 30px;
        background: #1f2937;
        border-radius: 15px;
        margin-top: 10px;
        overflow: hidden;
    }
    .bmi-gradient {
        height: 100%;
        width: 100%;
        background: linear-gradient(90deg, #3b82f6 0%, #10b981 30%, #f59e0b 60%, #ef4444 100%);
        opacity: 0.8;
    }
    .bmi-marker {
        position: absolute;
        top: 0;
        bottom: 0;
        width: 4px;
        background-color: white;
        box-shadow: 0 0 10px white;
        z-index: 10;
        transition: left 0.5s ease;
    }

    /* INPUTS & BUTTONS */
    .stSelectbox div[data-baseweb="select"] { cursor: pointer; }
    .stTextInput input, .stNumberInput input {
        background-color: #121212 !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
    
    /* PRIMARY BUTTON (Add) */
    .stButton button {
        background: #2563eb;
        color: white;
        border-radius: 6px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        border: none;
    }
    /* FINISH BUTTON (Green) */
    .finish-btn button {
        background: linear-gradient(90deg, #059669, #10b981) !important;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. GYM DATA (REAL NAMES) ---
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
    # Gym logic: Time under tension
    # Avg 1 rep = 3-4 seconds. 10 reps = 40s + rest.
    # Approx 2.5 mins per set total
    duration_min = sets * 2.5
    return round((met * 3.5 * weight) / 200 * duration_min, 1)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚡ TITAN PRO")
    st.caption("ADVANCED GYM TRACKER")
    st.markdown("---")
    
    st.markdown("### 👤 ATHLETE IDENTITY")
    name = st.text_input("Username", value="User")
    
    c1, c2 = st.columns(2)
    with c1: weight = st.number_input("Weight (kg)", 30.0, 200.0, 75.0)
    with c2: height = st.number_input("Height (m)", 1.0, 2.5, 1.75)
    
    bmi = weight / (height ** 2)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.connected:
        st.error("🔴 SYSTEM OFFLINE")
        if st.button("INITIALIZE SYSTEM"):
            st.session_state.connected = True
            st.rerun()
    else:
        st.success("🟢 SYSTEM ONLINE")
        if st.button("DISCONNECT"):
            st.session_state.connected = False
            st.rerun()

# --- 7. MAIN INTERFACE ---
if not st.session_state.connected:
    st.markdown("""
    <div style='height: 60vh; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #555;'>
        <h1 style='font-size: 4rem; color: #333 !important;'>LOCKED</h1>
        <p>AWAITING USER INITIALIZATION</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"<h1>WELCOME, {name.upper()}</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🚀 WORKOUT CONSOLE", "📊 PERFORMANCE DATA"])

    # --- TAB 1: WORKOUT CONSOLE ---
    with tab1:
        col_left, col_right = st.columns([1, 2], gap="large")

        # LEFT: ADVANCED BMI VISUAL
        with col_left:
            st.markdown('<div class="titan-card">', unsafe_allow_html=True)
            st.markdown("### 🧬 BIO-METRICS")
            
            # BMI Calc
            if bmi < 18.5: status, color = "UNDERWEIGHT", "#3b82f6"
            elif 18.5 <= bmi < 25: status, color = "OPTIMAL", "#10b981"
            elif 25 <= bmi < 30: status, color = "OVERWEIGHT", "#f59e0b"
            else: status, color = "CRITICAL", "#ef4444"
            
            st.markdown(f"<h2 style='color: {color} !important; margin:0;'>{bmi:.1f}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: {color} !important; font-weight:bold; letter-spacing: 2px;'>{status}</p>", unsafe_allow_html=True)

            # Custom CSS Progress Bar
            # Map BMI 10-40 to Percentage 0-100
            pct = max(0, min(100, (bmi - 10) / 30 * 100))
            
            st.markdown(f"""
            <div class="bmi-container">
                <div class="bmi-gradient"></div>
                <div class="bmi-marker" style="left: {pct}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #666; margin-top: 5px;">
                <span>10</span><span>18.5</span><span>25</span><span>30</span><span>40</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # RIGHT: LOGGING SYSTEM
        with col_right:
            st.markdown('<div class="titan-card">', unsafe_allow_html=True)
            st.markdown("### 📝 CURRENT SESSION")
            
            # Input Form
            with st.form("add_exercise_form", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1: ex_name = st.selectbox("Exercise", list(EXERCISES_DB.keys()))
                with c2: sets = st.number_input("Sets", 1, 10, 3)
                with c3: reps = st.number_input("Reps", 1, 50, 10)
                
                # "Add to Session" Button
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
                st.markdown("#### ⚡ ACTIVE STACK")
                
                for idx, item in enumerate(st.session_state.current_workout):
                    st.markdown(f"""
                    <div class="exercise-card">
                        <div style="display:flex; align-items:center; gap:15px;">
                            <span style="font-size: 1.5rem;">{item['Icon']}</span>
                            <div>
                                <div style="font-weight:bold; color:white;">{item['Module']}</div>
                                <div style="font-size:0.8rem; color:#aaa;">{item['Sets']} Sets × {item['Reps']} Reps</div>
                            </div>
                        </div>
                        <div style="color: #60a5fa; font-weight:bold;">+{item['Burn']} kcal</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- FINISH BUTTON ---
                # This button saves everything and clears the stack
                col_fin, _ = st.columns([1, 1])
                with col_fin:
                    st.markdown('<div class="finish-btn">', unsafe_allow_html=True)
                    if st.button("✅ FINISH & SAVE DAY"):
                        # Save to DB
                        st.session_state.history = save_session(st.session_state.current_workout)
                        # Clear Stack
                        st.session_state.current_workout = []
                        st.success("SESSION RECORDED SUCCESSFULLY")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            
            else:
                st.info("Stack is empty. Add an exercise to begin.")
                
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 2: ANALYTICS ---
    with tab2:
        st.markdown('<div class="titan-card">', unsafe_allow_html=True)
        st.markdown("### 📊 PERFORMANCE ANALYTICS")
        
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            
            # Summary Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Burn (All Time)", f"{int(df['Burn'].sum())} kcal")
            m2.metric("Total Sets", int(df['Sets'].sum()))
            m3.metric("Total Reps", int(df['Reps'].sum()))
            
            st.markdown("---")
            
            # Graph
            chart_data = df.groupby("Date")['Burn'].sum().reset_index()
            fig = px.bar(chart_data, x="Date", y="Burn", 
                         title="Calorie Burn History",
                         template="plotly_dark",
                         color="Burn", color_continuous_scale="teal")
            
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Rajdhani"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Data Table
            with st.expander("View Raw Data Logs"):
                st.dataframe(df, use_container_width=True)
                
        else:
            st.info("No data recorded yet. Complete a workout to see analytics.")
        
        st.markdown('</div>', unsafe_allow_html=True)
