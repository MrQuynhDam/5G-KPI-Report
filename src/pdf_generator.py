import io
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak, Image
)
from src.config import FONT_NAME

def generate_pdf_report(summary, hourly_trend_df, top10_sites, top10_cells, worst10_add_sr, worst10_drop, worst10_intra_ho, worst10_inter_ho, fb_cell_counts=None, fb_tf_df=None):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []
    
    t_style = ParagraphStyle("T", fontName=FONT_NAME, fontSize=16, textColor=colors.HexColor("#0f172a"), spaceAfter=4)
    h2_style = ParagraphStyle("H2", fontName=FONT_NAME, fontSize=11, textColor=colors.HexColor("#1e293b"), spaceBefore=8, spaceAfter=4)
    norm_style = ParagraphStyle("N", fontName=FONT_NAME, fontSize=8.5, textColor=colors.HexColor("#334155"))

    story.append(Paragraph("BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG MẠNG 5G", t_style))
    story.append(Paragraph(f"Thời gian xuất báo cáo: {pd.Timestamp.now().strftime('%d/%m/%Y')} | RNOC2", norm_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

    story.append(Paragraph("I. TỔNG QUAN KPI 5G", h2_style))
    # ... (giữ nguyên logic render Table Cards và Charts bằng Matplotlib như file cũ)
    
    doc.build(story)
    buf.seek(0)
    return buf
