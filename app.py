import streamlit as st
import tempfile
import os
from dotenv import load_dotenv
from app.main import run_pipeline

# ================== LOAD ENV ==================
load_dotenv()

APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Attendance Report",
    layout="centered"
)

# ================== SESSION STATE ==================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ================== LOGIN FUNCTION ==================
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid username or password")

# ================== AUTH GATE ==================
if not st.session_state.authenticated:
    login()
    st.stop()

# ================== LOGOUT ==================
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ================== MAIN APP ==================
st.title("📊 Attendance Report Generator")

procare_file = st.file_uploader(
    "Upload Procare Excel",
    type=["xls", "xlsx"]
)

dhs_file = st.file_uploader(
    "Upload DHS Excel",
    type=["xls", "xlsx"]
)

if st.button("▶️ Generate Report"):

    if not procare_file or not dhs_file:
        st.error("Please upload both Procare and DHS files.")
        st.stop()

    with st.spinner("Processing files..."):
        with tempfile.TemporaryDirectory() as tmpdir:

            procare_path = os.path.join(tmpdir, "procare.xlsx")
            dhs_path = os.path.join(tmpdir, "dhs.xlsx")
            output_path = os.path.join(tmpdir, "final_attendance.xlsx")

            with open(procare_path, "wb") as f:
                f.write(procare_file.read())

            with open(dhs_path, "wb") as f:
                f.write(dhs_file.read())

            run_pipeline(
                procare_file=procare_path,
                dhs_file=dhs_path,
                output_file=output_path
            )

            with open(output_path, "rb") as f:
                st.success("✅ Report generated successfully!")
                st.download_button(
                    label="⬇️ Download Report",
                    data=f,
                    file_name="final_attendance_output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
