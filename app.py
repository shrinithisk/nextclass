import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import base64
from io import BytesIO

# ============================================
# PAGE CONFIG & STYLING
# ============================================
st.set_page_config(
    page_title="Smart Classroom Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    :root {
        --primary-color: #00A86B;
        --secondary-color: #1e3a8a;
        --danger-color: #ef4444;
        --warning-color: #f59e0b;
        --success-color: #10b981;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
    }
    
    .alert-danger {
        background-color: #fee;
        border-left: 4px solid #ef4444;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .alert-success {
        background-color: #efe;
        border-left: 4px solid #10b981;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA LOADING & CACHING
# ============================================
@st.cache_data
def load_timetable():
    """Load and preprocess timetable data"""
    # IMPORTANT: Change this path to your CSV file location
    df = pd.read_csv("data/timetable - Sheet1.csv")
    
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()
    
    # Parse times
    df["start_time"] = pd.to_datetime(df["start_time"], format="%H:%M").dt.time
    df["end_time"] = pd.to_datetime(df["end_time"], format="%H:%M").dt.time
    
    # Clean whitespace
    df["lschool"] = df["lschool"].str.strip()
    df["faculty"] = df["faculty"].str.strip()
    df["course"] = df["course"].str.strip()
    
    return df

# ============================================
# UTILITY FUNCTIONS
# ============================================
def get_current_classes(df):
    """Get classes happening right now"""
    now = datetime.now()
    current_day = now.strftime("%A")
    current_time = now.time()
    
    ongoing = df[
        (df["day"] == current_day) &
        (df["start_time"] <= current_time) &
        (df["end_time"] >= current_time)
    ]
    return ongoing

def get_next_classes(df, limit=5):
    """Get next upcoming classes"""
    now = datetime.now()
    current_day = now.strftime("%A")
    current_time = now.time()
    
    today_classes = df[df["day"] == current_day].copy()
    upcoming = today_classes[today_classes["start_time"] > current_time]
    
    if len(upcoming) == 0:
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_idx = days_order.index(current_day) if current_day in days_order else 0
        tomorrow = days_order[(current_idx + 1) % 7]
        upcoming = df[df["day"] == tomorrow].copy()
    
    return upcoming.head(limit)

def get_free_rooms(df):
    """Get rooms not in use right now"""
    all_rooms = sorted(df["room"].dropna().astype(str).unique())
    ongoing = get_current_classes(df)
    occupied = set(ongoing["room"].dropna().astype(str))
    free = [r for r in all_rooms if r not in occupied]
    return free

def get_busy_rooms(df):
    """Get currently occupied rooms"""
    ongoing = get_current_classes(df)
    busy = sorted(ongoing["room"].dropna().astype(str).unique())
    return busy

def calculate_time_until_next_class(df):
    """Calculate minutes until next class"""
    now = datetime.now()
    current_day = now.strftime("%A")
    current_time = now.time()
    
    today_classes = df[df["day"] == current_day].copy()
    future_classes = today_classes[today_classes["start_time"] > current_time]
    
    if len(future_classes) > 0:
        next_start = future_classes.iloc[0]["start_time"]
        delta = datetime.combine(datetime.now().date(), next_start) - datetime.now()
        return max(0, int(delta.total_seconds() // 60))
    return None

def highlight_current(row):
    """Highlight current class rows"""
    now = datetime.now()
    current_day = now.strftime("%A")
    current_time = now.time()
    
    if row["day"] == current_day and row["start_time"] <= current_time <= row["end_time"]:
        return ["background-color: #d4edda; font-weight: bold;"] * len(row)
    return [""] * len(row)

def get_faculty_workload(df):
    """Calculate faculty class count and hours"""
    df_temp = df.copy()
    df_temp["duration_minutes"] = df_temp.apply(
        lambda x: int((datetime.combine(datetime.min, x["end_time"]) - 
                      datetime.combine(datetime.min, x["start_time"])).total_seconds() / 60),
        axis=1
    )
    
    workload = df_temp.groupby("faculty").agg({
        "course": "count",
        "duration_minutes": "sum"
    }).rename(columns={"course": "num_classes", "duration_minutes": "total_minutes"})
    
    workload["total_hours"] = (workload["total_minutes"] / 60).round(1)
    workload = workload.sort_values("total_hours", ascending=False)
    return workload

def detect_scheduling_conflicts(df):
    """Detect room conflicts (same room, same time)"""
    now = datetime.now()
    current_day = now.strftime("%A")
    
    today = df[df["day"] == current_day].copy()
    conflicts = []
    
    for idx, row in today.iterrows():
        overlapping = today[
            (today["room"] == row["room"]) &
            (today.index != idx) &
            (today["start_time"] < row["end_time"]) &
            (today["end_time"] > row["start_time"])
        ]
        
        if len(overlapping) > 0:
            for _, overlap_row in overlapping.iterrows():
                conflict = {
                    "Room": row["room"],
                    "Course 1": row["course"],
                    "Time 1": f"{row['start_time']} - {row['end_time']}",
                    "Faculty 1": row["faculty"],
                    "Course 2": overlap_row["course"],
                    "Time 2": f"{overlap_row['start_time']} - {overlap_row['end_time']}",
                    "Faculty 2": overlap_row["faculty"]
                }
                if conflict not in conflicts:
                    conflicts.append(conflict)
    
    return pd.DataFrame(conflicts) if conflicts else None

# ============================================
# MAIN APP
# ============================================
df = load_timetable()

# Sidebar Navigation
st.sidebar.title("🎓 Classroom Management System")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "📚 Classes", "🚪 Room Status", "👨‍🏫 Faculty", "⚠️ Conflicts", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Filters")
school_filter = st.sidebar.multiselect(
    "Filter by School",
    sorted(df["lschool"].unique()),
    default=sorted(df["lschool"].unique())
)

filtered_df = df[df["lschool"].isin(school_filter)].copy()

# ============================================
# PAGE: DASHBOARD
# ============================================
if page == "📊 Dashboard":
    st.title("📊 Classroom Management Dashboard")
    st.markdown("Real-time overview of all classes and resources")
    
    # Top Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "📚 Total Classes",
            len(filtered_df),
            "This week"
        )
    
    with col2:
        current_classes = get_current_classes(filtered_df)
        st.metric(
            "🎓 Ongoing Now",
            len(current_classes),
            f"{len(current_classes)} active"
        )
    
    with col3:
        free_rooms = get_free_rooms(filtered_df)
        st.metric(
            "🚪 Free Rooms",
            len(free_rooms),
            f"Out of {len(filtered_df['room'].unique())}"
        )
    
    with col4:
        unique_faculty = len(filtered_df["faculty"].unique())
        st.metric(
            "👨‍🏫 Faculty Members",
            unique_faculty,
            "Teaching this week"
        )
    
    with col5:
        minutes_until = calculate_time_until_next_class(filtered_df)
        if minutes_until is not None:
            hours = minutes_until // 60
            mins = minutes_until % 60
            st.metric(
                "⏰ Next Class",
                f"{hours}h {mins}m",
                "Time remaining"
            )
        else:
            st.metric("⏰ Next Class", "N/A", "No classes today")
    
    st.markdown("---")
    
    # Current Classes Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔴 Classes Happening Right Now")
        current = get_current_classes(filtered_df)
        
        if current.empty:
            st.info("✅ No classes happening right now. Campus is quiet!")
        else:
            display_cols = ["lschool", "course", "room", "faculty", "start_time", "end_time"]
            st.dataframe(
                current[display_cols],
                use_container_width=True,
                hide_index=True
            )
    
    with col2:
        st.subheader("📅 Next Classes")
        next_classes = get_next_classes(filtered_df, limit=5)
        
        if next_classes.empty:
            st.warning("No upcoming classes today")
        else:
            for idx, row in next_classes.iterrows():
                st.write(f"**{row['course']}**")
                st.caption(f"🕐 {row['start_time']} | 🚪 Room {row['room']} | 👨‍🏫 {row['faculty']}")

# ============================================
# PAGE: CLASSES
# ============================================
elif page == "📚 Classes":
    st.title("📚 Class Schedule")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        day_filter = st.selectbox(
            "Select Day",
            ["All"] + sorted(filtered_df["day"].unique())
        )
    
    with col2:
        course_search = st.text_input("🔍 Search Course Name")
    
    with col3:
        faculty_filter = st.multiselect(
            "Filter Faculty",
            sorted(filtered_df["faculty"].unique()),
            key="faculty_select"
        )
    
    # Apply filters
    result_df = filtered_df.copy()
    
    if day_filter != "All":
        result_df = result_df[result_df["day"] == day_filter]
    
    if course_search:
        result_df = result_df[result_df["course"].str.contains(course_search, case=False, na=False)]
    
    if faculty_filter:
        result_df = result_df[result_df["faculty"].isin(faculty_filter)]
    
    # Display results
    if result_df.empty:
        st.warning("No classes found matching your filters")
    else:
        display_cols = ["lschool", "course", "day", "start_time", "end_time", "room", "faculty"]
        st.dataframe(
            result_df[display_cols].style.apply(highlight_current, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown(f"**Found {len(result_df)} classes**")

# ============================================
# PAGE: ROOM STATUS
# ============================================
elif page == "🚪 Room Status":
    st.title("🚪 Room Availability & Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🟢 Free Rooms Right Now")
        free_rooms = get_free_rooms(filtered_df)
        
        if free_rooms:
            st.success(f"**{len(free_rooms)}** rooms available")
            st.write(", ".join(free_rooms))
        else:
            st.warning("❌ All rooms are occupied")
    
    with col2:
        st.subheader("🔴 Occupied Rooms Right Now")
        busy_rooms = get_busy_rooms(filtered_df)
        current = get_current_classes(filtered_df)
        
        if busy_rooms:
            st.info(f"**{len(busy_rooms)}** rooms in use")
            st.write(", ".join(busy_rooms))
        else:
            st.success("All rooms are free!")

# ============================================
# PAGE: FACULTY
# ============================================
elif page == "👨‍🏫 Faculty":
    st.title("👨‍🏫 Faculty Schedule & Workload")
    
    st.subheader("📋 Faculty Schedule Details")
    selected_faculty = st.selectbox("Select Faculty", sorted(filtered_df["faculty"].unique()))
    
    faculty_schedule = filtered_df[filtered_df["faculty"] == selected_faculty]
    st.dataframe(
        faculty_schedule[["lschool", "course", "day", "start_time", "end_time", "room"]],
        use_container_width=True,
        hide_index=True
    )
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Classes", len(faculty_schedule))
    
    with col2:
        total_mins = faculty_schedule.apply(
            lambda x: int((datetime.combine(datetime.min, x["end_time"]) - 
                          datetime.combine(datetime.min, x["start_time"])).total_seconds() / 60),
            axis=1
        ).sum()
        st.metric("Total Teaching Hours", f"{total_mins // 60}h {total_mins % 60}m")
    
    with col3:
        st.metric("Unique Courses", len(faculty_schedule["course"].unique()))

# ============================================
# PAGE: CONFLICTS
# ============================================
elif page == "⚠️ Conflicts":
    st.title("⚠️ Scheduling Conflicts Detection")
    
    st.info("🔍 Analyzing schedule for conflicts...")
    
    conflicts = detect_scheduling_conflicts(filtered_df)
    
    if conflicts is None or len(conflicts) == 0:
        st.success("✅ **No scheduling conflicts detected!** Schedule is clean.")
    else:
        st.error(f"⚠️ **Found {len(conflicts)} potential conflicts**")
        st.dataframe(conflicts, use_container_width=True)

# ============================================
# PAGE: SETTINGS & EXPORT
# ============================================
elif page == "⚙️ Settings":
    st.title("⚙️ Settings & Data Export")
    
    st.subheader("📥 Export Data")
    
    csv_data = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name="timetable.csv",
        mime="text/csv"
    )
    
    try:
        from openpyxl import Workbook
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, sheet_name='Timetable', index=False)
        buffer.seek(0)
        st.download_button(
            label="📥 Download Excel",
            data=buffer.getvalue(),
            file_name="timetable.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except:
        st.warning("Excel export requires: pip install openpyxl")
    
    st.markdown("---")
    
    st.subheader("📋 Raw Data Viewer")
    
    if st.checkbox("Show raw data", value=False):
        st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>📚 Smart Classroom Management System | Built with Streamlit</div>", unsafe_allow_html=True)
