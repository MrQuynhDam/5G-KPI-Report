import os
import streamlit as st
import pandas as pd

from src.config import setup_vietnamese_fonts, inject_custom_css
from src.data_loader import process_data
from src.ui_components import render_kpi_overview
from src.pdf_generator import generate_pdf_report

st.set_page_config(page_title="5G RAN Dashboard", page_icon="📶", layout="wide")
setup_vietnamese_fonts()
inject_custom_css()

st.sidebar.title("📶 Navigation (5G)")

sample_path = os.path.join("data", "5G_Sample.csv")
if os.path.exists(sample_path):
    with open(sample_path, "rb") as f:
        st.sidebar.download_button("📥 Tải File Mẫu (5G_Sample.csv)", f.read(), "5G_Sample.csv", "text/csv")

up_file = st.sidebar.file_uploader("📂 Tải CSV KPI 5G:", type=["csv"])

if up_file:
    df = process_data(up_file)
elif os.path.exists(sample_path):
    df = process_data(sample_path)
else:
    st.info("👋 Vui lòng tải file CSV KPI 5G.")
    st.stop()

st.title("📡 5G RAN Quality Report")
render_kpi_overview(df)
