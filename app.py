import streamlit as st
import tempfile
import os
import time
import json
import base64
from dotenv import load_dotenv
from streamlit_lottie import st_lottie
from app.main import run_pipeline

# ================== PATHS ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ================== LOAD ENV ==================
load_dotenv()
APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="🐝 Honeybee Attendance Engine",  # browser tab title
    layout="wide"
)

# ================== SESSION STATE ==================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# ================== HELPERS ==================
def load_lottie(filename: str):
    path = os.path.join(ASSETS_DIR, filename)
    with open(path, "r") as f:
        return json.load(f)

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

def show_logo():
    logo_path = os.path.join(ASSETS_DIR, "logo.png")

    if not os.path.exists(logo_path):
        st.error(f"❌ Logo bulunamadı: {logo_path}")
        return

    logo_b64 = encode_image_to_base64(logo_path)

    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: center;
            margin-top: 12px;
            margin-bottom: 12px;
        ">
            <img src="data:image/png;base64,{logo_b64}" width="160" />
        </div>
        """,
        unsafe_allow_html=True
    )

bee_anim = load_lottie("bee.json")
honey_anim = load_lottie("honeycomb.json")

# ================== LOGIN ==================
def login():
    show_logo()
    st.markdown("<br>", unsafe_allow_html=True)

    left, center, right = st.columns([2, 1.5, 2])

    with center:
        st.subheader("🔐 Login")

        username = st.text_input(
            "Username",
            placeholder="Enter username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Login", use_container_width=True):
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
_, logout_col = st.columns([6, 1])
with logout_col:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ================== PROGRESS ==================
def animated_progress():
    bar = st.progress(0)
    status = st.empty()

    steps = [
        ("🐝 Gathering files", 20),
        ("⚙️ Processing data", 45),
        ("🧮 Reconciling attendance", 70),
        ("📊 Generating report", 90),
        ("✅ Finalizing", 100),
    ]

    current = 0
    for text, target in steps:
        status.markdown(f"**{text}...**")
        while current < target:
            current += 1
            bar.progress(current)
            time.sleep(0.02)

# ================== MAIN LAYOUT ==================
left, center, right = st.columns([1.3, 3, 1.3])

# ---------- LEFT ANIMATION (VERTICALLY CENTERED) ----------
with left:
    st.markdown("<div style='height:140px'></div>", unsafe_allow_html=True)
    st_lottie(
        bee_anim,
        speed=0.8,
        loop=True,
        height=320
    )

# ---------- RIGHT ANIMATION (VERTICALLY CENTERED) ----------
with right:
    st.markdown("<div style='height:140px'></div>", unsafe_allow_html=True)
    st_lottie(
        honey_anim,
        speed=0.5,
        loop=True,
        height=320
    )

# ---------- CENTER APP ----------
with center:
    show_logo()

    # 🔹 PAGE TITLE (CENTERED)
    st.markdown(
        "<h1 style='text-align: center;'>🐝 Honeybee Attendance Engine</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align: center; color: gray;'>Automated attendance reconciliation</p>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    procare_file = st.file_uploader(
        "Upload Procare Excel",
        type=["xls", "xlsx"]
    )

    dhs_file = st.file_uploader(
        "Upload DHS Excel",
        type=["xls", "xlsx"]
    )

    if st.button(
        "▶️ Generate Report",
        disabled=st.session_state.is_processing
    ):
        if not procare_file or not dhs_file:
            st.error("❌ Please upload both Procare and DHS files.")
            st.stop()

        st.session_state.is_processing = True

        with tempfile.TemporaryDirectory() as tmpdir:
            animated_progress()

            procare_path = os.path.join(tmpdir, "procare.xlsx")
            dhs_path = os.path.join(tmpdir, "dhs.xlsx")
            output_path = os.path.join(tmpdir, "final_attendance.xlsx")

            with open(procare_path, "wb") as f:
                f.write(procare_file.read())

            with open(dhs_path, "wb") as f:
                f.write(dhs_file.read())

            try:
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

            except Exception as e:
                st.error(f"❌ Error: {e}")

        st.session_state.is_processing = False
