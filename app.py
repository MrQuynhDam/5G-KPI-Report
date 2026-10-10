import os
import pandas as pd
import streamlit as st

from src.config import setup_vietnamese_fonts, inject_custom_css
from src.data_loader import process_data
from src.ui_components import (
    render_kpi_overview,
    render_freqband_charts,
    render_trend_chart,
    render_top_n_section,
    render_worst_n_section,
    render_pdf_export_section,
)

# 1. Cấu hình trang & Font
st.set_page_config(
    page_title="5G RAN Dashboard",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded",
)
setup_vietnamese_fonts()
inject_custom_css()

# =========================================================
# 2. Sidebar Navigation & Data Upload
# =========================================================
st.sidebar.title("📶 Navigation (5G)")

sample_path = os.path.join("data", "5G_Sample.csv")
if os.path.exists(sample_path):
    with open(sample_path, "rb") as f:
        st.sidebar.download_button(
            "📥 Tải File Mẫu (5G_Sample.csv)",
            f.read(),
            "5G_Sample.csv",
            "text/csv",
        )

st.sidebar.markdown("---")
up_file = st.sidebar.file_uploader("📂 Tải CSV KPI 5G:", type=["csv"])

if up_file is not None:
    st.sidebar.success("✅ Đã tải file 5G!")
    df = process_data(up_file)
elif os.path.exists(sample_path):
    st.sidebar.info("ℹ️ Đang dùng dữ liệu mẫu 5G_Sample.csv")
    df = process_data(sample_path)
elif os.path.exists("5G_Sample.csv"):
    df = process_data("5G_Sample.csv")
else:
    st.info("👋 Vui lòng tải file CSV KPI 5G ở thanh công cụ bên trái.")
    st.stop()

# ---------------------------------------------------------
# 🚨 CHÈN VÀO ĐÂY: Dừng app an toàn nếu file nạp vào bị lỗi / sai định dạng
# ---------------------------------------------------------
if df is None:
    st.stop()

# =========================================================
# 3. Sidebar Filters (Các đoạn code phía dưới giữ nguyên)
# =========================================================
st.sidebar.subheader("📅 Chọn Ngày")
if "Date" in df.columns and df["Date"].notnull().any():
    ...

# 3. Sidebar Filters
st.sidebar.subheader("📅 Chọn Ngày")
if "Date" in df.columns and df["Date"].notnull().any():
    all_dates = sorted(df["Date"].dropna().unique().tolist())
    sel_dates = st.sidebar.multiselect(
        "Chọn Ngày",
        options=all_dates,
        default=all_dates,
        label_visibility="collapsed",
    )
else:
    all_dates = []
    sel_dates = []

st.sidebar.subheader("📡 Chọn GNODEB")
site_col = "Tên GNODEB" if "Tên GNODEB" in df.columns else None

if sel_dates and "Date" in df.columns:
    filtered_df = df[df["Date"].isin(sel_dates)]
else:
    filtered_df = df.copy()

if site_col and site_col in filtered_df.columns:
    all_sites = sorted(filtered_df[site_col].dropna().unique().tolist())
    sel_sites = st.sidebar.multiselect(
        "Chọn GNODEB",
        options=all_sites,
        default=all_sites,
        label_visibility="collapsed",
    )
    if sel_sites:
        filtered_df = filtered_df[filtered_df[site_col].isin(sel_sites)]

if filtered_df.empty:
    st.warning("⚠️ Không tìm thấy dữ liệu phù hợp!")
    st.stop()

# 4. Header & KPI Summary Cards
cell_col = "Tên CELL" if "Tên CELL" in filtered_df.columns else None
num_cells = filtered_df[cell_col].nunique() if cell_col else 0
num_sites = filtered_df[site_col].nunique() if site_col and site_col in filtered_df.columns else 0

st.title("📡 5G RAN Quality Report")
st.markdown(f"**Records:** `{len(filtered_df):,}` | **GNODEB:** `{num_sites}` | **5G Cells:** `{num_cells}`")
st.markdown("---")

# Render 10 KPI Cards
render_kpi_overview(filtered_df)
st.markdown("---")

# 5. Thống kê Freqband
render_freqband_charts(filtered_df, cell_col)
st.markdown("---")

# 6. Biểu đồ xu hướng Plotly
render_trend_chart(filtered_df)
st.markdown("---")

# 7. Top N High Traffic
top_cell_df, top_site_df = render_top_n_section(filtered_df, site_col, cell_col)
st.markdown("---")

# 8. Worst N Cells
worst10_add_sr, worst10_drop, worst10_intra_ho, worst10_inter_ho = render_worst_n_section(filtered_df, site_col, cell_col)
st.markdown("---")

# 9. Xuất Báo Cáo PDF
has_hour_info = ("Hour" in filtered_df.columns and filtered_df["Hour"].notna().any())
render_pdf_export_section(
    filtered_df,
    site_col,
    cell_col,
    top_site_df,
    top_cell_df,
    worst10_add_sr,
    worst10_drop,
    worst10_intra_ho,
    worst10_inter_ho,
    has_hour_info
)
