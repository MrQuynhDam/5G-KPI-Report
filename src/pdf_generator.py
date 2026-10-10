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
    
    t_style = ParagraphStyle("T", fontName=FONT_NAME, fontSize=16, textColor=colors.HexColor("#0f172a"), spaceAfter=6)
    h2_style = ParagraphStyle("H2", fontName=FONT_NAME, fontSize=11, textColor=colors.HexColor("#1e293b"), spaceBefore=8, spaceAfter=4)
    norm_style = ParagraphStyle("N", fontName=FONT_NAME, fontSize=8.5, textColor=colors.HexColor("#334155"))

    def p_cell(text, is_bold=False, align='left', color_hex='#0f172a'):
        p_st = ParagraphStyle('PC', fontName=FONT_NAME, fontSize=7.5, textColor=colors.HexColor(color_hex), leading=9, alignment=0 if align=='left' else 1)
        txt = f"<b>{text}</b>" if is_bold else str(text)
        return Paragraph(txt, p_st)

    now_str = pd.Timestamp.now().strftime("%d/%m/%Y")

    # HEADER BÁO CÁO
    story.append(Paragraph("BÁO CÁO CHẤT LƯỢNG MẠNG 5G", t_style))
    story.append(Paragraph(f"Thời gian xuất báo cáo: {now_str}", norm_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

    # MỤC I. TỔNG QUAN KPI 5G
    story.append(Paragraph("I. TỔNG QUAN KPI 5G", h2_style))
    story.append(Spacer(1, 4))

    card_t_style = ParagraphStyle('CT', fontName=FONT_NAME, fontSize=7.5, textColor=colors.HexColor('#475569'), leading=9)
    card_v_style = ParagraphStyle('CV', fontName=FONT_NAME, fontSize=13, textColor=colors.HexColor('#0f172a'), leading=15)
    card_s_style = ParagraphStyle('CS', fontName=FONT_NAME, fontSize=6.5, textColor=colors.HexColor('#64748b'), leading=8)

    def create_pdf_card(cat, title, val, target, remark, color_hex="#10b981"):
        p_t = Paragraph(f"<b>{cat.upper()}</b><br/>{title}", card_t_style)
        p_v = Paragraph(f"<font color='{color_hex}'><b>{val}</b></font>", card_v_style)
        p_s = Paragraph(f"<b>Target:</b> {target}<br/><i>{remark}</i>", card_s_style)
        
        c_tbl = Table([[p_t], [p_v], [p_s]], colWidths=[142])
        c_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        return c_tbl

    cards_row1 = [
        create_pdf_card("Data Traffic", "Total 5G Traffic", f"{summary.get('tf',0):,.2f} GB", "N/A", "Tải dữ liệu 5G", "#2563eb"),
        create_pdf_card("Accessibility", "SgNB Add SR", f"{summary.get('add_sr',0):.2f}%", ">=99.00%", "Thiết lập SgNB", "#059669" if summary.get('add_sr',0)>=99.0 else "#d97706"),
        create_pdf_card("Retainability", "SgNB Abn Drop Rate", f"{summary.get('drop',0):.3f}%", "<=1.000%", "Tỷ lệ rớt SgNB", "#059669" if summary.get('drop',0)<=1.0 else "#dc2626"),
        create_pdf_card("Integrity", "User DL Throughput", f"{summary.get('dl',0):.2f} M", ">100.0M", "Tốc độ DL 5G", "#059669" if summary.get('dl',0)>100 else "#d97706"),
        create_pdf_card("Integrity", "User UL Throughput", f"{summary.get('ul',0):.2f} M", ">=1.5M", "Tốc độ UL 5G", "#059669" if summary.get('ul',0)>=1.5 else "#d97706"),
    ]

    cards_row2 = [
        create_pdf_card("Radio Quality", "CQI 5G Index", f"{summary.get('cqi',0):.2f}%", ">=95.00%", "Chất lượng RF 5G", "#059669" if summary.get('cqi',0)>=95 else "#d97706"),
        create_pdf_card("Capacity & Load", "PRB DL Utilization", f"{summary.get('prb_dl',0):.2f}%", "<=40.00%", "Tải PRB Downlink", "#059669" if summary.get('prb_dl',0)<=40 else "#dc2626"),
        create_pdf_card("Capacity & Load", "PRB UL Utilization", f"{summary.get('prb_ul',0):.2f}%", "<=40.00%", "Tải PRB Uplink", "#059669" if summary.get('prb_ul',0)<=40 else "#dc2626"),
        create_pdf_card("Mobility", "Intra-SgNB HO SR", f"{summary.get('intra',0):.2f}%", ">=98.00%", "Chuyển giao nội bộ", "#059669" if summary.get('intra',0)>=98 else "#d97706"),
        create_pdf_card("Mobility", "Inter-SgNB HO SR", f"{summary.get('inter',0):.2f}%", ">=98.00%", "Chuyển giao liên SgNB", "#059669" if summary.get('inter',0)>=98 else "#d97706"),
    ]

    grid_cards = Table([cards_row1, cards_row2], colWidths=[150]*5)
    grid_cards.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 1),
        ('RIGHTPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(grid_cards)
    story.append(Spacer(1, 8))

    # MỤC II. THỐNG KÊ PHÂN BỔ CELL VÀ TRAFFIC
    if (fb_cell_counts is not None and not fb_cell_counts.empty) or (fb_tf_df is not None and not fb_tf_df.empty):
        story.append(Paragraph("II. THỐNG KÊ PHÂN BỔ CELL VÀ TRAFFIC", h2_style))
        story.append(Spacer(1, 2))
        
        # 1. BẢNG BỔ SUNG: Thống kê chi tiết số lượng Cell và Traffic theo Băng tần
        merged_fb = pd.DataFrame()
        if fb_cell_counts is not None and not fb_cell_counts.empty:
            merged_fb = fb_cell_counts.copy()
            if fb_tf_df is not None and not fb_tf_df.empty:
                merged_fb = pd.merge(merged_fb, fb_tf_df, on="Freqband", how="left").fillna(0)
            else:
                merged_fb["TRAFFIC"] = 0.0
        elif fb_tf_df is not None and not fb_tf_df.empty:
            merged_fb = fb_tf_df.copy()
            merged_fb["Số lượng Cell"] = 0

        if not merged_fb.empty:
            total_cells_count = merged_fb["Số lượng Cell"].sum()
            fb_table_data = [[
                p_cell("Băng tần (Freqband)", True, color_hex='#ffffff'),
                p_cell("Số lượng Cell", True, color_hex='#ffffff'),
                p_cell("Tỷ lệ Cell (%)", True, color_hex='#ffffff'),
                p_cell("Tổng Traffic (GB)", True, color_hex='#ffffff')
            ]]
            
            for _, r in merged_fb.iterrows():
                cnt = int(r.get("Số lượng Cell", 0))
                pct = (cnt / total_cells_count * 100) if total_cells_count > 0 else 0
                tf = float(r.get("TRAFFIC", 0))
                fb_table_data.append([
                    p_cell(str(r.get("Freqband", ""))),
                    p_cell(f"{cnt:,}"),
                    p_cell(f"{pct:.1f}%"),
                    p_cell(f"{tf:,.2f}")
                ])
            
            tot_tf = merged_fb["TRAFFIC"].sum() if "TRAFFIC" in merged_fb else 0
            fb_table_data.append([
                p_cell("Tổng cộng", True),
                p_cell(f"{total_cells_count:,}", True),
                p_cell("100.0%", True),
                p_cell(f"{tot_tf:,.2f}", True)
            ])

            t_fb = Table(fb_table_data, colWidths=[180, 180, 180, 180])
            t_fb.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0284c7")),
                ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#f1f5f9")),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
                ("TOPPADDING", (0,0), (-1,-1), 3),
                ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0,1), (-1,-2), [colors.white, colors.HexColor("#f8fafc")]),
            ]))
            story.append(t_fb)
            story.append(Spacer(1, 6))

        # 2. Biểu đồ hình tròn và biểu đồ cột
        fb_img_buf = io.BytesIO()
        fig_fb, (ax1_fb, ax2_fb) = plt.subplots(1, 2, figsize=(11, 2.6), dpi=150)
        
        if fb_cell_counts is not None and not fb_cell_counts.empty:
            fb_labels = fb_cell_counts["Freqband"].tolist()
            fb_sizes = fb_cell_counts["Số lượng Cell"].tolist()
            fb_colors = ['#0284c7', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4']
            
            wedges, texts, autotexts = ax1_fb.pie(
                fb_sizes, labels=fb_labels, autopct='%1.1f%%', startangle=90,
                colors=fb_colors[:len(fb_labels)],
                wedgeprops=dict(width=0.45, edgecolor='white')
            )
            for t_idx, t in enumerate(texts):
                t.set_fontsize(7.5)
            for at in autotexts:
                at.set_fontsize(7)
                at.set_weight('bold')
            ax1_fb.set_title("Số lượng & Tỷ lệ Cell theo Băng tần", fontsize=8.5, fontweight='bold', pad=6)
        
        if fb_tf_df is not None and not fb_tf_df.empty:
            fb_bands = fb_tf_df["Freqband"].tolist()
            fb_traffics = fb_tf_df["TRAFFIC"].tolist()
            fb_bars = ax2_fb.bar(fb_bands, fb_traffics, color='#0284c7', width=0.45, alpha=0.85)
            ax2_fb.set_title("Tổng Traffic 5G (GB) theo Băng tần", fontsize=8.5, fontweight='bold', pad=6)
            ax2_fb.set_ylabel("Traffic (GB)", fontsize=7.5)
            ax2_fb.tick_params(axis='both', labelsize=7)
            ax2_fb.grid(True, linestyle='--', alpha=0.25, axis='y')
            
            max_tf = max(fb_traffics) if fb_traffics else 1
            ax2_fb.set_ylim(0, max_tf * 1.18)
            
            for bar in fb_bars:
                yval = bar.get_height()
                ax2_fb.text(
                    bar.get_x() + bar.get_width()/2.0, 
                    yval + (max_tf * 0.02), 
                    f"{yval:,.1f} GB", 
                    ha='center', va='bottom', fontsize=6.5, fontweight='bold'
                )

        plt.tight_layout()
        plt.savefig(fb_img_buf, format='png', dpi=150)
        plt.close()
        fb_img_buf.seek(0)
        story.append(Image(fb_img_buf, width=740, height=175))
        story.append(Spacer(1, 10))

    # MỤC III. CÁC CHỈ SỐ KPI
    story.append(Paragraph("III. CÁC CHỈ SỐ KPI", h2_style))
    story.append(Spacer(1, 4))

    if not hourly_trend_df.empty:
        df_chart = hourly_trend_df.copy()
        x_labels = []
        for _, r in df_chart.iterrows():
            if "TimeLabel" in r and pd.notnull(r["TimeLabel"]) and str(r["TimeLabel"]).strip() != "":
                x_labels.append(str(r["TimeLabel"]))
            elif "DateTime" in r and pd.notnull(r["DateTime"]):
                x_labels.append(pd.to_datetime(r["DateTime"]).strftime("%d/%m %H:00"))
            elif "Date" in r and pd.notnull(r["Date"]):
                x_labels.append(pd.to_datetime(r["Date"]).strftime("%d/%m"))
            else:
                x_labels.append(f"{int(r.get('Hour', 0)):02d}:00")
        n_pts = len(x_labels)
        step = max(1, n_pts // 24)

        tf_vals = df_chart.get("TRAFFIC", pd.Series([0]*n_pts)).values
        add_vals = df_chart.get("SGNB_ADD_SUCCESS_RATE", pd.Series([0]*n_pts)).values
        drop_vals = df_chart.get("SGNB_ABN_RELEASE_RATE", pd.Series([0]*n_pts)).values
        dl_vals = df_chart.get("USER_DL_AVG_THROUGHPUT", pd.Series([0]*n_pts)).values
        intra_vals = df_chart.get("INTRA_SGNB_PS_CHANGE", pd.Series([0]*n_pts)).values
        inter_vals = df_chart.get("INTER_SGNB_PS_CHANGE", pd.Series([0]*n_pts)).values

        def make_single_chart(chart_title, bar_vals, line1_vals, line1_lbl, line1_color, 
                              line2_vals=None, line2_lbl=None, line2_color=None, 
                              bar_lbl="Traffic (GB)"):
            img_b = io.BytesIO()
            fig, ax = plt.subplots(figsize=(11, 3.568), dpi=150)

            ax.set_xticks(range(0, n_pts, step))
            ax.set_xticklabels([x_labels[i] for i in range(0, n_pts, step)], rotation=30 if n_pts > 15 else 0, ha='right' if n_pts > 15 else 'center', fontsize=6)
            ax.grid(True, linestyle='--', alpha=0.25)

            if bar_vals is not None:
                ax.bar(range(n_pts), bar_vals, color='#0284c7', alpha=0.45, label=bar_lbl, width=0.8)
                ax.set_ylabel(bar_lbl, color='#0284c7', fontweight='bold', fontsize=7.5)
                ax.tick_params(axis='y', labelcolor='#0284c7', labelsize=6.5)

            if line2_vals is None:
                ax_t = ax.twinx() if bar_vals is not None else ax
                ax_t.plot(range(n_pts), line1_vals, color=line1_color, marker='o', markersize=2.5, linewidth=1.4, label=line1_lbl)
                ax_t.set_ylabel(line1_lbl, color=line1_color, fontweight='bold', fontsize=7.5)
                ax_t.tick_params(axis='y', labelcolor=line1_color, labelsize=6.5)
            else:
                ax.plot(range(n_pts), line1_vals, color=line1_color, marker='o', markersize=2.5, linewidth=1.4, label=line1_lbl)
                ax.plot(range(n_pts), line2_vals, color=line2_color, marker='s', markersize=2.5, linewidth=1.4, linestyle='--', label=line2_lbl)
                ax.set_ylabel("Handover SR (%)", color='#0f172a', fontweight='bold', fontsize=7.5)
                ax.set_ylim(80, 100.5)
                ax.legend(fontsize=6.5, loc='lower right')

            ax.set_title(chart_title, fontsize=8.5, fontweight='bold', pad=4)
            plt.tight_layout()
            plt.savefig(img_b, format='png', dpi=150)
            plt.close()
            img_b.seek(0)
            return Image(img_b, width=740, height=240)

        c1_img = make_single_chart("Chart 1: SgNB Add Success Rate (%) & Data Traffic 5G (GB)", tf_vals, add_vals, "SgNB Add SR (%)", "#10b981")
        story.append(c1_img)
        story.append(Spacer(1, 8))

        c2_img = make_single_chart("Chart 2: SgNB Abn Release Rate (%) & Data Traffic 5G (GB)", tf_vals, drop_vals, "SgNB Drop Rate (%)", "#ef4444")
        story.append(c2_img)
        story.append(Spacer(1, 8))

        story.append(PageBreak())

        c3_img = make_single_chart("Chart 3: Download Throughput 5G (Mbps) & Data Traffic (GB)", tf_vals, dl_vals, "DL Thrp 5G (Mbps)", "#8b5cf6")
        story.append(c3_img)
        story.append(Spacer(1, 8))

        c4_img = make_single_chart("Chart 4: Intra-SgNB HO (%) vs Inter-SgNB HO (%)", None, intra_vals, "Intra-SgNB HO (%)", "#059669", line2_vals=inter_vals, line2_lbl="Inter-SgNB HO (%)", line2_color="#d97706")
        story.append(c4_img)
        story.append(Spacer(1, 8))

    story.append(PageBreak())

    # MỤC IV. TOP 10 HIGH TRAFFIC
    story.append(Paragraph("IV. DANH SÁCH TOP 10 HIGH TRAFFIC GNODEB & CELL (5G)", h2_style))
    story.append(Spacer(1, 4))

    if not top10_cells.empty:
        story.append(Paragraph("<b>1. Top 10 Cell 5G có Lưu lượng Traffic Volume (GB) cao nhất:</b>", norm_style))
        story.append(Spacer(1, 2))
        
        tr_data = [[
            p_cell("Tên GNODEB", True, color_hex='#ffffff'),
            p_cell("Tên CELL", True, color_hex='#ffffff'),
            p_cell("Total Traffic (GB)", True, color_hex='#ffffff'),
            p_cell("DL Thrp (Mbps)", True, color_hex='#ffffff'),
            p_cell("PRB DL (%)", True, color_hex='#ffffff')
        ]]
        for _, row in top10_cells.head(10).iterrows():
            tr_data.append([
                p_cell(row.get("Tên GNODEB", "")),
                p_cell(row.get("Tên CELL", "")),
                p_cell(f"{row.get('TRAFFIC', 0):,.2f}"),
                p_cell(f"{row.get('USER_DL_AVG_THROUGHPUT', 0):.2f}"),
                p_cell(f"{row.get('DLINK_RES_BLK_ULT', 0):.2f}")
            ])

        t_tr = Table(tr_data, colWidths=[130, 180, 110, 110, 110])
        t_tr.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0284c7")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(t_tr)
        story.append(Spacer(1, 8))

    if not top10_sites.empty:
        story.append(Paragraph("<b>2. Top 10 GNODEB có Lưu lượng Traffic Volume (GB) cao nhất:</b>", norm_style))
        story.append(Spacer(1, 2))

        ts_data = [[
            p_cell("Tên GNODEB", True, color_hex='#ffffff'),
            p_cell("Total Traffic (GB)", True, color_hex='#ffffff'),
            p_cell("DL Thrp Avg (Mbps)", True, color_hex='#ffffff'),
            p_cell("PRB DL Avg (%)", True, color_hex='#ffffff')
        ]]
        for _, row in top10_sites.head(10).iterrows():
            ts_data.append([
                p_cell(row.get("Tên GNODEB", "")),
                p_cell(f"{row.get('TRAFFIC', 0):,.2f}"),
                p_cell(f"{row.get('USER_DL_AVG_THROUGHPUT', 0):.2f}"),
                p_cell(f"{row.get('DLINK_RES_BLK_ULT', 0):.2f}")
            ])

        t_ts = Table(ts_data, colWidths=[180, 150, 150, 160])
        t_ts.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0369a1")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(t_ts)
        story.append(Spacer(1, 10))

    story.append(PageBreak())

    # MỤC V. WORST 10 CELLS
    story.append(Paragraph("V. DANH SÁCH WORST 10 CELLS CHO CÁC KPI CHÍNH 5G", h2_style))
    story.append(Spacer(1, 4))

    if not worst10_add_sr.empty:
        story.append(Paragraph("<b>1. Worst 10 Cells theo Tỷ lệ SgNB Addition SR Thấp:</b>", norm_style))
        story.append(Spacer(1, 2))
        w_data = [[
            p_cell("Tên GNODEB", True, color_hex='#ffffff'),
            p_cell("Tên CELL", True, color_hex='#ffffff'),
            p_cell("SgNB Add SR (%)", True, color_hex='#ffffff'),
            p_cell("Total Traffic (GB)", True, color_hex='#ffffff')
        ]]
        for _, row in worst10_add_sr.head(10).iterrows():
            w_data.append([
                p_cell(row.get("Tên GNODEB", "")),
                p_cell(row.get("Tên CELL", "")),
                p_cell(f"{row.get('SGNB_ADD_SUCCESS_RATE', 0):.2f}%"),
                p_cell(f"{row.get('TRAFFIC', 0):,.2f}")
            ])
        t_cssr = Table(w_data, colWidths=[180, 220, 170, 170])
        t_cssr.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#991b1b")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(t_cssr)
        story.append(Spacer(1, 8))

    if not worst10_drop.empty:
        story.append(Paragraph("<b>2. Worst 10 Cells theo Tỷ lệ SgNB Abnormal Release Rate Cao:</b>", norm_style))
        story.append(Spacer(1, 2))
        w_data = [[
            p_cell("Tên GNODEB", True, color_hex='#ffffff'),
            p_cell("Tên CELL", True, color_hex='#ffffff'),
            p_cell("SgNB Abn Release (%)", True, color_hex='#ffffff'),
            p_cell("Total Traffic (GB)", True, color_hex='#ffffff')
        ]]
        for _, row in worst10_drop.head(10).iterrows():
            w_data.append([
                p_cell(row.get("Tên GNODEB", "")),
                p_cell(row.get("Tên CELL", "")),
                p_cell(f"{row.get('SGNB_ABN_RELEASE_RATE', 0):.3f}%"),
                p_cell(f"{row.get('TRAFFIC', 0):,.2f}")
            ])
        t_dcr = Table(w_data, colWidths=[180, 220, 170, 170])
        t_dcr.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#b91c1c")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(t_dcr)
        story.append(Spacer(1, 8))

    if not worst10_intra_ho.empty:
        story.append(Paragraph("<b>3. Worst 10 Cells theo Intra-SgNB HO SR Thấp:</b>", norm_style))
        story.append(Spacer(1, 2))
        w_data = [[
            p_cell("Tên GNODEB", True, color_hex='#ffffff'),
            p_cell("Tên CELL", True, color_hex='#ffffff'),
            p_cell("Intra-SgNB HO (%)", True, color_hex='#ffffff'),
            p_cell("Total Traffic (GB)", True, color_hex='#ffffff')
        ]]
        for _, row in worst10_intra_ho.head(10).iterrows():
            w_data.append([
                p_cell(row.get("Tên GNODEB", "")),
                p_cell(row.get("Tên CELL", "")),
                p_cell(f"{row.get('INTRA_SGNB_PS_CHANGE', 0):.2f}%"),
                p_cell(f"{row.get('TRAFFIC', 0):,.2f}")
            ])
        t_ho = Table(w_data, colWidths=[180, 220, 170, 170])
        t_ho.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#c2410c")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(t_ho)
        story.append(Spacer(1, 8))

    if not worst10_inter_ho.empty:
        story.append(Paragraph("<b>4. Worst 10 Cells theo Inter-SgNB HO SR Thấp:</b>", norm_style))
        story.append(Spacer(1, 2))
        w_data = [[
            p_cell("Tên GNODEB", True, color_hex='#ffffff'),
            p_cell("Tên CELL", True, color_hex='#ffffff'),
            p_cell("Inter-SgNB HO (%)", True, color_hex='#ffffff'),
            p_cell("Total Traffic (GB)", True, color_hex='#ffffff')
        ]]
        for _, row in worst10_inter_ho.head(10).iterrows():
            w_data.append([
                p_cell(row.get("Tên GNODEB", "")),
                p_cell(row.get("Tên CELL", "")),
                p_cell(f"{row.get('INTER_SGNB_PS_CHANGE', 0):.2f}%"),
                p_cell(f"{row.get('TRAFFIC', 0):,.2f}")
            ])
        t_inter_ho = Table(w_data, colWidths=[180, 220, 170, 170])
        t_inter_ho.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#ea580c")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(t_inter_ho)

    doc.build(story)
    buf.seek(0)
    return buf
