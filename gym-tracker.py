import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GymTracker Pro",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. EXERCISE DATABASE ---
EXERCISES = {
    "Push Ups": 3.8,
    "Squats": 5.0,
    "Running (Jog)": 7.0,
    "Bench Press": 6.0,
    "Pull Ups": 8.0,
    "Plank": 3.0,
    "Deadlift": 6.0,
    "Cycling": 7.5,
    "Jumping Jacks": 8.0,
    "Lunges": 4.0,
    "Bicep Curls": 3.5,
    "Burpees": 8.0,
    "Yoga": 2.5,
    "Swimming": 6.0,
    "Sit Ups": 3.8,
    "Shoulder Press": 5.5,
    "Rowing": 7.0,
    "Boxing": 9.0
}

# --- 3. SESSION STATE (Local Storage Logic) ---
if 'log' not in st.session_state:
    st.session_state.log = []

# --- 4. FUNCTIONS ---
def calculate_calories(met, weight, sets, reps):
    # Estimate: 1 set approx 2 mins
    duration_min = sets * 2
    if reps > 15: duration_min *= 1.2
    cals = (met * 3.5 * weight) / 200 * duration_min
    return round(cals, 1)

# --- 5. SIDEBAR (User Profile) ---
with st.sidebar:
    st.title("👤 User Profile")
    name = st.text_input("Name", "Student User")
    age = st.number_input("Age", 18, 100, 20)
    height = st.number_input("Height (m)", 1.0, 2.5, 1.75)
    weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
    
    # Quick BMI Calc
    bmi = weight / (height ** 2)
    st.markdown("---")
    st.markdown("### 📥 Data Controls")
    
    # Feature: Download Data as CSV
    if st.session_state.log:
        df = pd.DataFrame(st.session_state.log)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Workout Log (CSV)",
            data=csv,
            file_name="gym_log.csv",
            mime="text/csv",
        )

# --- 6. MAIN DASHBOARD ---
st.title(f"💪 GymTracker Pro")
st.markdown(f"Welcome back, **{name}**! Let's crush some goals.")

# Create two columns: Left for BMI, Right for Actions
col1, col2 = st.columns([1, 2])

with col1:
    # --- PLOTLY GAUGE CHART (Visual Appeal) ---
    st.markdown("### Your Health Status")
    
    # Determine Color
    if bmi < 18.5: color = "lightblue"
    elif 18.5 <= bmi < 25: color = "lightgreen"
    elif 25 <= bmi < 30: color = "orange"
    else: color = "red"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = bmi,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "BMI Score"},
        gauge = {
            'axis': {'range': [10, 40]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 18.5], 'color': "lightblue"},
                {'range': [18.5, 25], 'color': "lightgreen"},
                {'range': [25, 30], 'color': "orange"},
                {'range': [30, 40], 'color': "red"}
            ],
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)
    
    # Status Text
    status = "Healthy Weight"
    if bmi < 18.5: status = "Underweight"
    elif bmi >= 25: status = "Overweight"
    st.info(f"Status: **{status}**")

with col2:
    # --- WORKOUT LOGGER ---
    st.markdown("### 📝 Log a Workout")
    
    with st.form("workout_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            exercise = st.selectbox("Select Exercise", list(EXERCISES.keys()))
        with c2:
            sets = st.number_input("Sets", 1, 10, 3)
        with c3:
            reps = st.number_input("Reps", 1, 50, 10)
            
        submitted = st.form_submit_button("Add Entry")
        
        if submitted:
            met = EXERCISES[exercise]
            cals = calculate_calories(met, weight, sets, reps)
            
            # Add to local session
            st.session_state.log.append({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Exercise": exercise,
                "Sets": sets,
                "Reps": reps,
                "Calories Burned": cals
            })
            st.success(f"Added {exercise}! Burned approx {cals} kcal.")

# --- 7. HISTORY & METRICS ---
st.divider()

if st.session_state.log:
    # Metrics Row
    df = pd.DataFrame(st.session_state.log)
    total_cals = df['Calories Burned'].sum()
    total_sets = df['Sets'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Workouts", len(df))
    m2.metric("Total Calories Burned", f"{total_cals} kcal")
    m3.metric("Total Sets Completed", total_sets)
    
    # Data Table
    st.markdown("### 📜 Session History")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No workouts logged yet. Use the form above to start tracking!")