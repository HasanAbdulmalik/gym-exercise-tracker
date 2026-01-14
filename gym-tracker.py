import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os

st.set_page_config(
    page_title="Titan Pro Gym Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@400;600&display=swap');
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0f172a 0%, #020617 60%, #000000 100%);
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Rajdhani', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #e5e7eb !important;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
    }

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
        transition: all 0.3s ease;
    }
    .titan-card:hover {
        border-color: rgba(59, 130, 246, 0.5);
        box-shadow: 0 0 30px rgba(59, 130, 246, 0.2);
        transform: translateY(-2px);
    }

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

    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    .stTextInput input:hover, .stNumberInput input:hover, .stSelectbox div[data-baseweb="select"]:hover {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.2) !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.4) !important;
    }
    
    .stSelectbox div[data-baseweb="select"], 
    .stSelectbox div[data-baseweb="select"] *,
    .stSelectbox div[role="combobox"],
    .stSelectbox input {
        cursor: pointer !important;
    }

    div[data-testid="stForm"] button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stForm"] button:hover {
        box-shadow: 0 0 25px rgba(37, 99, 235, 0.7) !important;
        transform: scale(1.02) !important;
    }

    .finish-btn button {
        background: linear-gradient(135deg, #059669, #047857) !important;
    }
    .finish-btn button:hover {
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.6) !important;
    }

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

    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stDecoration"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        color: #3b82f6 !important;
        background-color: rgba(15, 23, 42, 0.8);
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 4px;
        margin-top: 10px;
        margin-left: 10px;
    }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

EXERCISES_DB = {
    "Barbell Squat": {"met": 6.0, "icon": "🏋️‍♂️"},
    "Bench Press": {"met": 5.0, "icon": "💪"},
    "Deadlift": {"met": 6.0, "icon": "🔋"},
    "Overhead Press": {"met": 5.0, "icon": "🆙"},
    "Barbell Row": {"met": 5.5, "icon": "🚣"},
    "Lat Pulldown": {"met": 4.0, "icon": "🔽"},
    "Dumbbell Lunges": {"met": 5.0, "icon": "🦵"},
    "Incline Bench": {"met": 5.0, "icon": "📐"},
    "Bicep Curls": {"met": 3.5, "icon": "💪"},
    "Tricep Extensions": {"met": 3.5, "icon": "🦾"},
}

def calculate_calories(met, weight, sets, reps):
    duration_min = sets * 2.5
    return round((met * 3.5 * weight) / 200 * duration_min, 1)

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
        if st.button("INITIALIZE UPLINK"):
            st.session_state.connected = True
            st.rerun()
    else:
        st.success("🟢 ONLINE")
        if st.button("TERMINATE UPLINK"):
            st.session_state.connected = False
            st.rerun()

if not st.session_state.connected:
    st.markdown("""
    <div style='height: 60vh; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #4b5563;'>
        <h1 style='font-size: 5rem; color: #1f2937 !important; text-shadow:none; opacity:0.5;'>LOCKED</h1>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"<h1 style='font-size:3rem; margin-bottom:10px;'>WELCOME, <span style='color:#3b82f6;'>{name.upper()}</span></h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🚀 SESSION REPORT", "📊 DATA ARCHIVE"])

    with tab1:
        col_left, col_right = st.columns([1, 2], gap="large")

        with col_left:
            st.markdown('<div class="titan-card">', unsafe_allow_html=True)
            st.markdown("### 🧬 BIO-STATUS")
            
            if bmi < 18.5: status, color = "UNDERWEIGHT", "#60a5fa"
            elif 18.5 <= bmi < 25: status, color = "OPTIMAL", "#34d399"
            elif 25 <= bmi < 30: status, color = "OVERWEIGHT", "#fbbf24"
            else: status, color = "CRITICAL", "#f87171"
            
            st.markdown(f"<h1 style='color: {color} !important; font-size: 4rem; margin:0; line-height:1;'>{bmi:.1f}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: {color} !important; font-weight:bold; letter-spacing: 3px; font-size:0.9rem;'>CONDITION: {status}</p>", unsafe_allow_html=True)

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

        with col_right:
            st.markdown('<div class="titan-card">', unsafe_allow_html=True)
            st.markdown("### 📝 ACTIVE SESSION")
            
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
                
                col_fin, _ = st.columns([1, 1])
                with col_fin:
                    st.markdown('<div class="finish-btn">', unsafe_allow_html=True)
                    if st.button("✅ COMPLETE SESSION & SAVE"):
                        st.session_state.history = save_session(st.session_state.current_workout)
                        st.session_state.current_workout = []
                        st.success("SAVED TO ARCHIVE")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("STACK EMPTY. UPDATE YOUR WORKOUTS.")
            
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="titan-card">', unsafe_allow_html=True)
        st.markdown("### 📊 PERFORMANCE GRAPH")
        
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            
            daily_df = daily_df = df.groupby("Date")['Burn'].sum().reset_index()
            daily_df = daily_df.sort_values("Date")
            
            daily_df['Change'] = daily_df['Burn'].diff()
            daily_df['Change'] = daily_df['Change'].fillna(1)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_df['Date'], 
                y=daily_df['Burn'],
                mode='lines+markers',
                line=dict(color='#00ff00', width=3),
                marker=dict(size=8, color='white', line=dict(width=2, color='#00ff00')),
                fill='tozeroy',
                fillcolor='rgba(0, 255, 0, 0.1)',
                name='Energy Output'
            ))

            fig.update_layout(
                title="ENERGY OUTPUT (KCALS)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Rajdhani", color="white"),
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='rgba(255,255,255,0.1)',
                    zeroline=False
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='rgba(255,255,255,0.1)',
                    zeroline=False
                ),
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("TOTAL CALORIES BURNED (KCAL)", f"{int(df['Burn'].sum())}")
            m2.metric("VOLUME (SETS)", int(df['Sets'].sum()))
            m3.metric("VOLUME (REPS)", int(df['Reps'].sum()))
            
            with st.expander("ACCESS LOG ENTRIES"):
                st.dataframe(df, use_container_width=True)
                
        else:
            st.info("NO LOG DATA AVAILABLE.")
        
        st.markdown('</div>', unsafe_allow_html=True)

