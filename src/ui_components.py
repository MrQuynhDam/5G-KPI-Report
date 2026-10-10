import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.data_loader import calc_weighted_avg

def render_card(cat, title, val, tgt, min_v, max_v, remark, stt="good"):
    s_low = stt.lower()
    html_str = (
        f'<div class="kpi-card"><div class="kpi-hdr"><div>'
        f'<div class="kpi-cat">{cat}</div><div class="kpi-ttl">{title}</div></div>'
        f'<span class="kpi-bdg bdg-{s_low}">{stt.upper()}</span></div>'
        f'<div class="kpi-body"><span class="kpi-val val-{s_low}">{val}</span>'
        f'<span class="kpi-tgt">Target: {tgt}</span></div>'
        f'<div class="kpi-ftr"><span>Min: {min_v} Max: {max_v}</span>'
        f'<span>{remark}</span></div></div>'
    )
    st.markdown(html_str, unsafe_allow_html=True)

def render_kpi_overview(filtered_df):
    s_tf = filtered_df.get("TRAFFIC", pd.Series([0]))
    s_add_sr = filtered_df.get("SGNB_ADD_SUCCESS_RATE", pd.Series([0]))
    s_drop = filtered_df.get("SGNB_ABN_RELEASE_RATE", pd.Series([0]))
    s_dl = filtered_df.get("USER_DL_AVG_THROUGHPUT", pd.Series([0]))
    s_ul = filtered_df.get("USER_UL_AVG_THROUGHPUT", pd.Series([0]))

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_card("5G Traffic", "Total 5G Traffic", f"{s_tf.sum():,.2f} GB", "N/A", f"{s_tf.min():.1f}G", f"{s_tf.max():.1f}G", "Tổng tải 5G", "EXCELLENT")
    with c2:
        v = calc_weighted_avg(filtered_df, "SGNB_ADD_SUCCESS_RATE")
        render_card("Accessibility", "SgNB Add SR", f"{v:.2f}%", ">=99.0%", f"{s_add_sr.min():.1f}%", f"{s_add_sr.max():.1f}%", "Thiết lập SgNB", "GOOD" if v >= 99.0 else "WARNING")
    with c3:
        v = calc_weighted_avg(filtered_df, "SGNB_ABN_RELEASE_RATE")
        render_card("Retainability", "SgNB Abn Drop", f"{v:.3f}%", "<=1.0%", f"{s_drop.min():.3f}%", f"{s_drop.max():.3f}%", "Tỷ lệ rớt 5G", "WARNING" if v > 1.0 else "GOOD")
    with c4:
        v = calc_weighted_avg(filtered_df, "USER_DL_AVG_THROUGHPUT")
        render_card("Integrity", "User DL Throughput", f"{v:.2f} M", ">100M", f"{s_dl.min():.1f}M", f"{s_dl.max():.1f}M", "Tốc độ DL 5G", "EXCELLENT" if v > 100.0 else "GOOD")
    with c5:
        v = calc_weighted_avg(filtered_df, "USER_UL_AVG_THROUGHPUT")
        render_card("Integrity", "User UL Throughput", f"{v:.2f} M", ">=1.5M", f"{s_ul.min():.2f}M", f"{s_ul.max():.2f}M", "Tốc độ UL 5G", "EXCELLENT" if v >= 1.5 else "GOOD")
