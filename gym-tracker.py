import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit_shadcn_ui as ui
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Titan Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DATA & LOGIC ---
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

# --- 3. SIDEBAR (User Profile) ---
with st.sidebar:
    st.title("⚡ TITAN PRO")
    ui.badges(badge_list=[("Pilot Mode", "default"), ("v1.0.0", "outline")], class_name="flex gap-2", key="badges")
    
    st.markdown("---")
    st.markdown("### 👤 User Profile")
    name = st.text_input("Username", "TitanUser")
    weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
    height = st.number_input("Height (m)", 1.0, 2.5, 1.75)
    
    # Calculate BMI
    bmi = weight / (height ** 2)
    
    st.markdown("---")
    # Export Button styled nicely
    if st.session_state.log:
        df = pd.DataFrame(st.session_state.log)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export CSV", csv, "titan_log.csv", "text/csv", use_container_width=True)

# --- 4. MAIN DASHBOARD ---

# Header Section
ui.card(title=f"Welcome back, {name}", content="Ready to crush your goals?", description=datetime.now().strftime("%A, %d %B %Y"), key="header_card").render()

# Layout Grid
col1, col2 = st.columns([1.5, 2.5])

with col1:
    st.markdown("### 🩺 Health Status")
    
    # Determine Health State
    if bmi < 18.5: 
        state_color = "blue"
        state_label = "Underweight"
    elif 18.5 <= bmi < 25: 
        state_color = "green"
        state_label = "Healthy"
    elif 25 <= bmi < 30: 
        state_color = "orange"
        state_label = "Overweight"
    else: 
        state_color = "red"
        state_label = "Obese"

    # Use a Shadcn Metric Card for BMI
    ui.metric_card(
        title="BMI Index",
        content=f"{bmi:.1f}",
        description=f"Status: {state_label}",
        key="bmi_card"
    ).render()

    # Visual Gauge (Plotly fits inside the column nicely)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = bmi,
        gauge = {
            'axis': {'range': [10, 40]},
            'bar': {'color': state_color},
            'bgcolor': "white",
            'steps': [
                {'range': [0, 18.5], 'color': "#e0f2fe"}, # light blue
                {'range': [18.5, 25], 'color': "#dcfce7"}, # light green
                {'range': [25, 30], 'color': "#ffedd5"}, # light orange
                {'range': [30, 40], 'color': "#fee2e2"}  # light red
            ],
        }
    ))
    fig.update_layout(height=250, margin=dict(t=10,b=10,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### ⚡ Command Console")
    
    # The Input Form wrapped in a container for "Card" look
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            exercise = st.selectbox("Select Module", list(EXERCISES.keys()))
        with c2:
            sets = st.number_input("Sets", 1, 10, 3)
        with c3:
            reps = st.number_input("Reps", 1, 50, 10)
        
        # Primary Action Button
        if ui.button("Log Activity", key="log_btn", variant="primary"):
            cals = calculate_calories(EXERCISES[exercise], weight, sets, reps)
            st.session_state.log.append({
                "Time": datetime.now().strftime("%H:%M"),
                "Exercise": exercise,
                "Sets": sets,
                "Reps": reps,
                "Burn": cals
            })
            st.rerun() # Refresh to show new stats immediately

# --- 5. STATISTICS ROW ---
st.markdown("### 📊 Mission Analytics")

if st.session_state.log:
    df = pd.DataFrame(st.session_state.log)
    total_cals = df['Burn'].sum()
    total_sets = df['Sets'].sum()
    total_sessions = len(df)
    
    # Three Metric Cards in a row using Shadcn UI
    cols = st.columns(3)
    with cols[0]:
        ui.metric_card(title="Total Burn", content=f"{total_cals} kcal", description="Estimated energy expenditure", key="m1").render()
    with cols[1]:
        ui.metric_card(title="Volume", content=f"{total_sets} sets", description="Total resistance volume", key="m2").render()
    with cols[2]:
        ui.metric_card(title="Sessions", content=f"{total_sessions}", description="Exercises completed today", key="m3").render()

    # Data Table styled
    st.markdown("<br>", unsafe_allow_html=True)
    ui.table(data=df, key="history_table")

else:
    # Empty State (Styled Alert)
    ui.alert(title="No Activity Detected", description="Log your first exercise above to initialize analytics.", variant="secondary", key="alert").render()
