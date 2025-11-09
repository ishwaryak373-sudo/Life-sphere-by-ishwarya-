# Filename: universal_dashboard_basic.py
import streamlit as st
import pandas as pd
import pickle
from datetime import date
import plotly.express as px
import random
import os

# -------------------------------
# Safe data file location (same folder as the app)
# -------------------------------
DATA_FILE = "dashboard_data_basic.pkl"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            # if corrupted, start fresh
            return {"tasks": [], "notes": [], "habits": [], "mood_log": []}
    else:
        return {"tasks": [], "notes": [], "habits": [], "mood_log": []}

def save_data(data):
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

# -------------------------------
# App setup
# -------------------------------
st.set_page_config(page_title="Universal Dashboard (Basic)", layout="wide")
st.title("🌐 Universal Dashboard — Basic")

# Load or initialize data
data = load_data()

# Sidebar controls
st.sidebar.header("App Controls")
theme = st.sidebar.selectbox("Theme", ["Auto", "Light", "Dark"])
if theme == "Dark":
    st.markdown(
        """<style>
        .css-18e3th9 { background-color: #0b0f14; }
        .st-bk { color: #ffffff; }
        </style>""",
        unsafe_allow_html=True
    )

st.sidebar.write("Persistent storage: `dashboard_data_basic.pkl`")
if st.sidebar.button("Reset all data"):
    data = {"tasks": [], "notes": [], "habits": [], "mood_log": []}
    save_data(data)
    st.sidebar.success("All data cleared. Refresh the page.")

# -------------------------------
# Section: Tasks
# -------------------------------
st.header("📋 Tasks")
with st.expander("Add a new task", expanded=False):
    task_name = st.text_input("Task name", key="new_task_name")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"], key="new_task_priority")
    due_date = st.date_input("Due date", value=date.today(), key="new_task_due")
    add_task = st.button("Add task", key="add_task_btn")
    if add_task:
        if not task_name.strip():
            st.warning("Please enter a task name.")
        else:
            data['tasks'].append({
                "name": task_name.strip(),
                "priority": priority,
                "due": due_date.isoformat(),
                "status": "Pending",
            })
            save_data(data)
            st.success("Task added.")
            st.experimental_rerun()

if data.get("tasks"):
    for i, t in enumerate(data["tasks"]):
        status = t.get("status", "Pending")
        with st.expander(f"{t['name']} — {status} (Priority: {t.get('priority','-')})", expanded=False):
            st.write(f"**Due:** {t.get('due','-')}")
            cols = st.columns([1,1,1])
            if cols[0].button(f"Mark Done ✅ {i}"):
                data["tasks"][i]["status"] = "Completed"
                save_data(data)
                st.experimental_rerun()
            if cols[1].button(f"Edit ✏️ {i}"):
                # simple inline edit modal-like
                new_name = st.text_input("Edit name", value=t["name"], key=f"edit_name_{i}")
                new_priority = st.selectbox("Edit priority", ["Low","Medium","High"], index=["Low","Medium","High"].index(t.get("priority","Low")), key=f"edit_prio_{i}")
                new_due = st.date_input("Edit due date", value=date.fromisoformat(t.get("due", date.today().isoformat())), key=f"edit_due_{i}")
                new_status = st.selectbox("Status", ["Pending","Completed"], index=0 if t.get("status","Pending")=="Pending" else 1, key=f"edit_status_{i}")
                if st.button("Save changes", key=f"save_{i}"):
                    data["tasks"][i].update({
                        "name": new_name.strip(),
                        "priority": new_priority,
                        "due": new_due.isoformat(),
                        "status": new_status
                    })
                    save_data(data)
                    st.success("Task updated.")
                    st.experimental_rerun()
            if cols[2].button(f"Delete ❌ {i}"):
                data["tasks"].pop(i)
                save_data(data)
                st.experimental_rerun()
else:
    st.info("No tasks yet. Use the 'Add a new task' panel to create one.")

# -------------------------------
# Section: Notes
# -------------------------------
st.header("📝 Notes")
with st.expander("Write a new note", expanded=False):
    note_title = st.text_input("Title", key="note_title")
    note_body = st.text_area("Note (supports plain text)", key="note_body")
    if st.button("Save note", key="save_note_btn"):
        if not note_title.strip() or not note_body.strip():
            st.warning("Please provide both a title and content for the note.")
        else:
            data.setdefault("notes", []).append({
                "title": note_title.strip(),
                "content": note_body.strip(),
                "date": date.today().isoformat()
            })
            save_data(data)
            st.success("Note saved.")
            st.experimental_rerun()

if data.get("notes"):
    for j, n in enumerate(reversed(data["notes"])):
        idx = len(data["notes"]) - 1 - j
        with st.expander(f"{n['title']} — {n['date']}", expanded=False):
            st.write(n["content"])
            if st.button(f"Delete Note ❌ {idx}"):
                data["notes"].pop(idx)
                save_data(data)
                st.experimental_rerun()
else:
    st.info("No notes yet. Add one above.")

# -------------------------------
# Section: Habits
# -------------------------------
st.header("🔥 Habits")
with st.expander("Add a habit", expanded=False):
    habit_name = st.text_input("Habit name", key="habit_name")
    if st.button("Add habit", key="add_habit_btn"):
        if habit_name.strip():
            data.setdefault("habits", []).append({"name": habit_name.strip(), "streak": 0})
            save_data(data)
            st.success("Habit added.")
            st.experimental_rerun()
        else:
            st.warning("Enter a habit name.")

if data.get("habits"):
    for h_idx, h in enumerate(data["habits"]):
        cols = st.columns([4,1])
        cols[0].write(f"{h['name']} — Streak: {h['streak']}")
        if cols[1].button(f"Mark today ✅ {h_idx}"):
            data["habits"][h_idx]["streak"] = data["habits"][h_idx].get("streak",0) + 1
            save_data(data)
            st.experimental_rerun()
else:
    st.info("No habits yet. Add one to start tracking streaks.")

# -------------------------------
# Section: Mood Tracker
# -------------------------------
st.header("😊 Mood Tracker")
mood_options = ["😢 Sad", "😐 Meh", "🙂 Good", "😃 Great", "🤩 Awesome"]
mood = st.select_slider("How are you feeling today?", options=mood_options, value=mood_options[2], key="mood_slider")
if st.button("Log mood", key="log_mood_btn"):
    data.setdefault("mood_log", []).append({"date": date.today().isoformat(), "mood": mood})
    save_data(data)
    st.success("Mood logged.")
    st.experimental_rerun()

if data.get("mood_log"):
    df_mood = pd.DataFrame(data["mood_log"])
    # map to numeric score
    mapping = {mood_options[i]: i+1 for i in range(len(mood_options))}
    df_mood["score"] = df_mood["mood"].map(mapping)
    try:
        fig = px.line(df_mood, x="date", y="score", title="Mood over time")
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.write(df_mood)
else:
    st.info("No mood entries yet. Log today's mood above.")

# -------------------------------
# Section: Dashboard Summary
# -------------------------------
st.header("📊 Snapshot")
total_tasks = len(data.get("tasks", []))
completed = sum(1 for t in data.get("tasks", []) if t.get("status") == "Completed")
pending = total_tasks - completed
total_notes = len(data.get("notes", []))
total_habits = len(data.get("habits", []))

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Tasks total", total_tasks)
col_b.metric("Tasks completed", completed)
col_c.metric("Notes", total_notes)
col_d.metric("Habits", total_habits)

# Ensure save
save_data(data)
