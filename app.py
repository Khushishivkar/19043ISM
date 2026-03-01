import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# ---------------- DATABASE CONNECTION ----------------
conn = sqlite3.connect("service_desk.db", check_same_thread=False)
cursor = conn.cursor()

# ---------------- CREATE TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    issue TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT,
    resolved_at TEXT
)
""")
conn.commit()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="IT Service Desk", page_icon="💻", layout="wide")

st.title("💻 IT Service Desk Management System")

# ---------------- SIDEBAR MENU ----------------
menu = st.sidebar.selectbox(
    "Select Option",
    ["Create Ticket", "View Tickets", "Close Ticket"]
)

# ====================================================
# CREATE TICKET
# ====================================================
if menu == "Create Ticket":

    st.subheader("📌 Create New Ticket")

    user = st.text_input("User Name")
    issue = st.text_area("Issue Description")
    priority = st.selectbox("Priority Level", ["Low", "Medium", "High"])

    if st.button("Submit Ticket"):

        if user.strip() == "" or issue.strip() == "":
            st.error("⚠ Please fill all fields")
        else:
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
            INSERT INTO tickets (user_name, issue, priority, status, created_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (user, issue, priority, "Open", created_at, ""))

            conn.commit()
            st.success("✅ Ticket Created Successfully!")

# ====================================================
# VIEW TICKETS
# ====================================================
elif menu == "View Tickets":

    st.subheader("📋 All Tickets")

    cursor.execute("SELECT * FROM tickets")
    rows = cursor.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=[
            "Ticket ID",
            "User Name",
            "Issue",
            "Priority",
            "Status",
            "Created At",
            "Resolved At"
        ])

        st.dataframe(df, use_container_width=True)

        # Dashboard Section
        st.subheader("📊 Ticket Summary")

        open_count = df[df["Status"] == "Open"].shape[0]
        closed_count = df[df["Status"] == "Closed"].shape[0]

        col1, col2 = st.columns(2)
        col1.metric("Open Tickets", open_count)
        col2.metric("Closed Tickets", closed_count)

    else:
        st.info("No Tickets Found")

# ====================================================
# CLOSE TICKET
# ====================================================
elif menu == "Close Ticket":

    st.subheader("🔒 Close Ticket")

    ticket_id = st.number_input("Enter Ticket ID", min_value=1, step=1)

    if st.button("Close Ticket"):

        resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE tickets
        SET status = ?, resolved_at = ?
        WHERE id = ? AND status = 'Open'
        """, ("Closed", resolved_at, ticket_id))

        conn.commit()

        if cursor.rowcount > 0:
            st.success("✅ Ticket Closed Successfully!")
        else:
            st.error("⚠ Invalid Ticket ID or Ticket Already Closed")