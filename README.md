
# 📚 Smart Classroom Management System

A **real-time classroom and timetable analytics platform** built using **Streamlit and Python**, designed to eliminate manual spreadsheet checking by providing instant insights into class schedules, room availability, faculty workload, and scheduling conflicts.

This project solves a **real-world university problem** where classrooms and room allocations frequently change and students must constantly verify updated timetables.

---

## 🚀 Key Features

### 📊 Intelligent Dashboard

* Displays **ongoing classes**, **upcoming classes**, and **time until next class**
* High-level metrics for total classes, faculty count, and room usage

### 🚪 Real-Time Room Availability

* Instantly identifies **free** and **occupied** classrooms
* Helps students find available rooms without manual checking

### 📚 Advanced Class Search & Filtering

* Filter by **day**, **school**, **faculty**, and **course name**
* Highlights classes happening **right now**

### 👨‍🏫 Faculty Workload Analytics

* Individual faculty schedules
* Total teaching hours and number of classes
* Useful for workload balancing and academic planning

### ⚠️ Automatic Conflict Detection

* Detects **room clashes** (same room, overlapping times)
* Prevents scheduling errors before they impact students

### 📥 Data Export

* Export filtered timetable data as **CSV** or **Excel**
* Enables offline analysis and reporting

---

## 🧠 Why This Project Matters

**Problem:**
Universities often publish timetables as spreadsheets that change frequently, forcing students to manually recheck class locations before every lecture.

**Solution:**
This system converts raw timetable data into an **interactive, intelligent web application** that provides **instant answers**, reduces confusion, and improves campus resource utilization.

---

## 🛠 Tech Stack

* **Python**
* **Streamlit** – Web application framework
* **Pandas & NumPy** – Data processing
* **Plotly** – Interactive visualizations
* **OpenPyXL** – Excel export support

---

## 📂 Project Structure

```
smart-classroom-management-system/
│
├── app.py                  # Main Streamlit application
├── data/
│   └── timetable.csv       # Sample timetable dataset
│
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
├── .gitignore
└── screenshots/            # Application screenshots (optional)
```

---

## ▶️ How to Run the Project Locally

```bash
# Clone the repository
git clone https://github.com/your-username/smart-classroom-management-system.git

# Navigate to the project folder
cd smart-classroom-management-system

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

---

## 📸 Screenshots


```md
![Dashboard](screenshots/dashboard.png)
![Room Status](screenshots/rooms.png)
![Faculty Analytics](screenshots/faculty.png)
```

---

## 🔍 Sample Use Cases

* Students checking **where their next class is**
* Finding **free classrooms** in real time
* Faculty reviewing their weekly teaching load
* Administrators detecting **room scheduling conflicts**

---

## 📈 Future Enhancements

* Chatbot interface (e.g., *“Where is my Linear Algebra class?”*)
* Authentication for students and faculty
* Live database integration (PostgreSQL / Firebase)
* Deployment with Streamlit Cloud or Docker
* Mobile-friendly UI optimization

---

## 👩‍💻 Author

**Shrinithi Saravanakumar**
Engineering Student | Python & Data Enthusiast




