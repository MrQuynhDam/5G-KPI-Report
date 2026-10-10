import os
import matplotlib
import streamlit as st
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

FONT_NAME = "VietFont"
FONT_NAME_BOLD = "VietFont-Bold"

def setup_vietnamese_fonts():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_reg = os.path.join(base_dir, "assets", "fonts", "DejaVuSans.ttf")
    local_bold = os.path.join(base_dir, "assets", "fonts", "DejaVuSans-Bold.ttf")

    if os.path.exists(local_reg):
        bold_path = local_bold if os.path.exists(local_bold) else local_reg
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, local_reg))
            pdfmetrics.registerFont(TTFont(FONT_NAME_BOLD, bold_path))
            for f in [FONT_NAME, FONT_NAME_BOLD]:
                addMapping(f, 0, 0, f)
                addMapping(f, 1, 0, FONT_NAME_BOLD)
                addMapping(f, 0, 1, f)
                addMapping(f, 1, 1, FONT_NAME_BOLD)
            matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
            matplotlib.rcParams["axes.unicode_minus"] = False
            return local_reg, bold_path, "DejaVu Sans"
        except Exception:
            pass

    return None, None, "Helvetica"

def inject_custom_css():
    st.markdown("""
    <style>
        .main { background: #0b0e14; }
        div[data-testid="stSidebar"] { background: #11151f; }
        .kpi-card { background: #131823; border: 1px solid #1f2738; border-radius: 8px; padding: 8px 10px; margin-bottom: 6px; color: #e0e6ed; }
        .kpi-hdr { display: flex; justify-content: space-between; align-items: flex-start; }
        .kpi-cat { font-size: 9px; color: #8b9bb4; font-weight: 500; }
        .kpi-ttl { font-size: 11px; font-weight: 700; color: #fff; line-height: 1.2; }
        .kpi-bdg { font-size: 8px; font-weight: 800; padding: 1px 4px; border-radius: 3px; }
        .bdg-excellent { background: rgba(16,185,129,0.2); color: #10b981; border: 1px solid #10b981; }
        .bdg-good { background: rgba(6,182,212,0.2); color: #06b6d4; border: 1px solid #06b6d4; }
        .bdg-warning { background: rgba(245,158,11,0.2); color: #f59e0b; border: 1px solid #f59e0b; }
        .kpi-body { display: flex; justify-content: space-between; align-items: baseline; margin: 3px 0; }
        .kpi-val { font-size: 18px; font-weight: 800; }
        .val-excellent, .val-good { color: #10b981; }
        .val-warning { color: #f59e0b; }
        .kpi-tgt { font-size: 9px; color: #a0aec0; }
        .kpi-ftr { display: flex; justify-content: space-between; border-top: 1px solid #1a2233; padding-top: 3px; font-size: 8.5px; color: #718096; }
    </style>
    """, unsafe_allow_html=True)
