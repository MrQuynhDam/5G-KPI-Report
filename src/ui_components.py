import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_loader import calc_weighted_avg
from src.pdf_generator import generate_pdf_report

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
    s_cqi = filtered_df.get("CQI_5G", pd.Series([0]))
    s_prb_dl = filtered_df.get("DLINK_RES_BLK_ULT", pd.Series([0]))
    s_prb_ul = filtered_df.get("ULINK_RES_BLK_ULT", pd.Series([0]))
    s_intra = filtered_df.get("INTRA_SGNB_PS_CHANGE", pd.Series([0]))
    s_inter = filtered_df.get("INTER_SGNB_PS_CHANGE", pd.Series([0]))

    # HÀNG 1 (5 CỘT)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        v = s_tf.sum()
        render_card("5G Traffic", "Total 5G Traffic", f"{v:,.2f} GB", "N/A", f"{s_tf.min():.1f}G", f"{s_tf.max():.1f}G", "Tổng tải 5G", "EXCELLENT")
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

    # HÀNG 2 (5 CỘT)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        v = calc_weighted_avg(filtered_df, "CQI_5G")
        render_card("Radio Quality", "CQI 5G Index", f"{v:.2f}%", ">=95.0%", f"{s_cqi.min():.1f}%", f"{s_cqi.max():.1f}%", "Chất lượng RF 5G", "EXCELLENT" if v >= 95.0 else "WARNING")
    with c2:
        v = calc_weighted_avg(filtered_df, "DLINK_RES_BLK_ULT")
        render_card("Capacity & Load", "PRB DL Utilization", f"{v:.2f}%", "<=40.0%", f"{s_prb_dl.min():.1f}%", f"{s_prb_dl.max():.1f}%", "Tải PRB Downlink", "EXCELLENT" if v <= 40.0 else "WARNING")
    with c3:
        v = calc_weighted_avg(filtered_df, "ULINK_RES_BLK_ULT")
        render_card("Capacity & Load", "PRB UL Utilization", f"{v:.2f}%", "<=40.0%", f"{s_prb_ul.min():.1f}%", f"{s_prb_ul.max():.1f}%", "Tải PRB Uplink", "EXCELLENT" if v <= 40.0 else "WARNING")
    with c4:
        v = s_intra.mean()
        render_card("Mobility", "Intra-SgNB HO SR", f"{v:.2f}%", ">=98.0%", f"{s_intra.min():.1f}%", f"{s_intra.max():.1f}%", "Chuyển giao nội bộ", "WARNING" if v < 98.0 else "GOOD")
    with c5:
        v = s_inter.mean()
        render_card("Mobility", "Inter-SgNB HO SR", f"{v:.2f}%", ">=98.0%", f"{s_inter.min():.1f}%", f"{s_inter.max():.1f}%", "Chuyển giao liên SgNB", "WARNING" if v < 98.0 else "GOOD")

def render_freqband_charts(filtered_df, cell_col):
    st.subheader("📊 Thống Kê Phân Bổ Cell & Traffic Theo Freqband (5G)")
    fb_col1, fb_col2 = st.columns(2)

    if cell_col and "Freqband" in filtered_df.columns:
        cell_fb_df = filtered_df[[cell_col, "Freqband"]].drop_duplicates()
        fb_cell_counts = cell_fb_df["Freqband"].value_counts().reset_index()
        fb_cell_counts.columns = ["Freqband", "Số lượng Cell"]
        fb_cell_counts = fb_cell_counts.sort_values(by="Freqband")

        fig_fb_cell = px.pie(
            fb_cell_counts,
            names="Freqband",
            values="Số lượng Cell",
            title="<b>Tỷ lệ & Số lượng Cell theo Băng tần (5G)</b>",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_fb_cell.update_traces(textinfo="label+value+percent", textfont_size=12)
        fig_fb_cell.update_layout(template="plotly_dark", height=320, margin=dict(l=20, r=20, t=40, b=20))

        with fb_col1:
            st.plotly_chart(fig_fb_cell, use_container_width=True)

        if "TRAFFIC" in filtered_df.columns:
            fb_tf_df = filtered_df.groupby("Freqband")["TRAFFIC"].sum().reset_index()
            fb_tf_df = fb_tf_df.sort_values(by="Freqband")

            fig_fb_tf = px.bar(
                fb_tf_df,
                x="Freqband",
                y="TRAFFIC",
                text="TRAFFIC",
                title="<b>Tổng Traffic Volume (GB) theo Băng tần (5G)</b>",
                color="Freqband",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_fb_tf.update_traces(texttemplate='%{text:,.1f} GB', textposition='outside')
            fig_fb_tf.update_layout(
                template="plotly_dark",
                height=320,
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                yaxis_title="Traffic Volume (GB)",
                xaxis_title="Freqband"
            )

            with fb_col2:
                st.plotly_chart(fig_fb_tf, use_container_width=True)

def render_trend_chart(filtered_df):
    st.subheader("📈 Biểu Đồ Tương Quan Xu Hướng KPI 5G")

    kpi_dict = {
        "DL Throughput 5G (Mbps)": "USER_DL_AVG_THROUGHPUT",
        "UL Throughput 5G (Mbps)": "USER_UL_AVG_THROUGHPUT",
        "CQI 5G Index (%)": "CQI_5G",
        "PRB DL Utilization (%)": "DLINK_RES_BLK_ULT",
        "PRB UL Utilization (%)": "ULINK_RES_BLK_ULT",
        "SgNB Abn Release Rate (%)": "SGNB_ABN_RELEASE_RATE",
        "SgNB Add Success Rate (%)": "SGNB_ADD_SUCCESS_RATE",
        "Intra-SgNB HO SR (%)": "INTRA_SGNB_PS_CHANGE",
        "Inter-SgNB HO SR (%)": "INTER_SGNB_PS_CHANGE",
    }

    avail_kpis = {k: v for k, v in kpi_dict.items() if v in filtered_df.columns}
    has_hour_info = ("Hour" in filtered_df.columns and filtered_df["Hour"].notna().any())

    ctrl_col1, ctrl_col2 = st.columns([1, 1])
    with ctrl_col1:
        time_options = ["Chỉ theo giờ (24h Avg)", "Theo Ngày & Giờ (Timeline)"]
        time_mode = st.radio(
            "⏱ Thời gian:",
            options=time_options,
            index=1,
            disabled=not has_hour_info,
            horizontal=True
        )

    with ctrl_col2:
        sel_kpi_lbl = st.selectbox("🎯 Chọn KPI kết hợp Traffic 5G:", options=list(avail_kpis.keys()))

    sel_kpi_col = avail_kpis[sel_kpi_lbl]
    agg_func = "mean"

    if time_mode == "Chỉ theo giờ (24h Avg)" and has_hour_info:
        c_data = filtered_df.groupby("Hour").agg({
            "TRAFFIC": "sum",
            sel_kpi_col: agg_func,
            "USER_DL_AVG_THROUGHPUT": "mean",
            "USER_UL_AVG_THROUGHPUT": "mean",
            "SGNB_ABN_RELEASE_RATE": "mean",
            "SGNB_ADD_SUCCESS_RATE": "mean",
            "INTRA_SGNB_PS_CHANGE": "mean",
            "INTER_SGNB_PS_CHANGE": "mean",
            "DLINK_RES_BLK_ULT": "mean"
        }).reset_index()
        x_axis = c_data["Hour"].astype(int)
        x_title = "Giờ trong ngày (0h - 23h)"
    elif time_mode == "Theo Ngày & Giờ (Timeline)" and has_hour_info and "DateTime" in filtered_df.columns:
        c_data = filtered_df.groupby(["Date", "Hour", "DateTime"]).agg({
            "TRAFFIC": "sum",
            sel_kpi_col: agg_func,
            "USER_DL_AVG_THROUGHPUT": "mean",
            "USER_UL_AVG_THROUGHPUT": "mean",
            "SGNB_ABN_RELEASE_RATE": "mean",
            "SGNB_ADD_SUCCESS_RATE": "mean",
            "INTRA_SGNB_PS_CHANGE": "mean",
            "INTER_SGNB_PS_CHANGE": "mean",
            "DLINK_RES_BLK_ULT": "mean"
        }).reset_index().sort_values(by="DateTime")
        c_data["TimeLabel"] = c_data["DateTime"].dt.strftime("%d/%m %H:00")
        x_axis = c_data["TimeLabel"]
        x_title = "Thời Gian (Ngày/Giờ)"
    else:
        c_data = filtered_df.groupby("Date").agg({
            "TRAFFIC": "sum",
            sel_kpi_col: agg_func,
            "USER_DL_AVG_THROUGHPUT": "mean",
            "USER_UL_AVG_THROUGHPUT": "mean",
            "SGNB_ABN_RELEASE_RATE": "mean",
            "SGNB_ADD_SUCCESS_RATE": "mean",
            "INTRA_SGNB_PS_CHANGE": "mean",
            "INTER_SGNB_PS_CHANGE": "mean",
            "DLINK_RES_BLK_ULT": "mean"
        }).reset_index().sort_values(by="Date")
        c_data["TimeLabel"] = pd.to_datetime(c_data["Date"]).dt.strftime("%d/%m/%Y")
        x_axis = c_data["TimeLabel"]
        x_title = "Thời Gian (Ngày)"

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=x_axis, y=c_data["TRAFFIC"], name="Traffic 5G (GB)", marker_color="rgba(2, 132, 199, 0.5)"), secondary_y=False)
    fig.add_trace(go.Scatter(x=x_axis, y=c_data[sel_kpi_col], name=sel_kpi_lbl, mode="lines+markers", line=dict(color="#10b981", width=2.5)), secondary_y=True)

    fig.update_layout(title_text=f"📊 Biểu đồ Traffic và {sel_kpi_lbl}", template="plotly_dark", hovermode="x unified", height=420, margin=dict(l=10, r=10, t=40, b=10))
    fig.update_xaxes(title_text=x_title, type="category" if time_mode != "Chỉ theo giờ (24h Avg)" else None)
    fig.update_yaxes(title_text="Traffic (GB)", secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text=sel_kpi_lbl, secondary_y=True, showgrid=True, gridcolor="rgba(255,255,255,0.1)")

    st.plotly_chart(fig, use_container_width=True)

def render_top_n_section(filtered_df, site_col, cell_col):
    st.subheader("🔥 Top N GNODEB & Top N Cell 5G Có Lưu Lượng Cao Nhất")

    tr_col1, tr_col2 = st.columns([2, 1])
    with tr_col1:
        st.markdown("Lọc danh sách Top GNODEB và Top Cell 5G có tổng lưu lượng dữ liệu lớn nhất.")
    with tr_col2:
        top_n_traffic = st.number_input("🔢 Nhập số lượng Top N cần xem:", min_value=1, max_value=200, value=10, step=1)

    top_cell_df = pd.DataFrame()
    top_site_df = pd.DataFrame()

    if "TRAFFIC" in filtered_df.columns:
        tab_cell, tab_site = st.tabs(["📱 Top Cell Traffic (5G)", "🏢 Top GNODEB Traffic"])

        grp_cols = [site_col, cell_col] if site_col and cell_col else ([cell_col] if cell_col else [site_col])
        top_cell_df = (
            filtered_df.groupby(grp_cols)
            .agg({
                "TRAFFIC": "sum",
                "DL_TRAFFIC_VOLUME": "sum" if "DL_TRAFFIC_VOLUME" in filtered_df.columns else "mean",
                "UL_TRAFFIC_VOLUME": "sum" if "UL_TRAFFIC_VOLUME" in filtered_df.columns else "mean",
                "USER_DL_AVG_THROUGHPUT": "mean",
                "DLINK_RES_BLK_ULT": "mean",
            })
            .reset_index()
            .sort_values(by="TRAFFIC", ascending=False)
            .head(int(top_n_traffic))
        )

        with tab_cell:
            st.markdown(f"**Top {top_n_traffic} Cell 5G có lưu lượng cao nhất:**")
            st.dataframe(top_cell_df, use_container_width=True)

        if site_col:
            top_site_df = (
                filtered_df.groupby(site_col)
                .agg({
                    "TRAFFIC": "sum",
                    "DL_TRAFFIC_VOLUME": "sum" if "DL_TRAFFIC_VOLUME" in filtered_df.columns else "mean",
                    "UL_TRAFFIC_VOLUME": "sum" if "UL_TRAFFIC_VOLUME" in filtered_df.columns else "mean",
                    "USER_DL_AVG_THROUGHPUT": "mean",
                    "DLINK_RES_BLK_ULT": "mean",
                })
                .reset_index()
                .sort_values(by="TRAFFIC", ascending=False)
                .head(int(top_n_traffic))
            )
            with tab_site:
                st.markdown(f"**Top {top_n_traffic} GNODEB có lưu lượng cao nhất:**")
                st.dataframe(top_site_df, use_container_width=True)

    return top_cell_df, top_site_df

def render_worst_n_section(filtered_df, site_col, cell_col):
    st.subheader("⚠️ Danh Sách Worst N Cells Theo KPI 5G")

    if not cell_col:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    kpi_options_dict = {
        "SgNB Add Success Rate Thấp": ("SGNB_ADD_SUCCESS_RATE", True),
        "SgNB Abnormal Release Rate Cao": ("SGNB_ABN_RELEASE_RATE", False),
        "Intra-SgNB HO SR Thấp": ("INTRA_SGNB_PS_CHANGE", True),
        "Inter-SgNB HO SR Thấp": ("INTER_SGNB_PS_CHANGE", True),
        "User DL Throughput Thấp": ("USER_DL_AVG_THROUGHPUT", True),
        "User UL Throughput Thấp": ("USER_UL_AVG_THROUGHPUT", True),
        "CQI 5G Thấp": ("CQI_5G", True),
        "PRB DL Utilization Cao": ("DLINK_RES_BLK_ULT", False),
        "PRB UL Utilization Cao": ("ULINK_RES_BLK_ULT", False),
    }

    available_kpi_options = {lbl: (col, is_asc) for lbl, (col, is_asc) in kpi_options_dict.items() if col in filtered_df.columns}

    kpi_col1, kpi_col2 = st.columns([2, 1])
    with kpi_col1:
        sel_worst_kpi_lbl = st.selectbox("🎯 Chọn KPI cần xem:", options=list(available_kpi_options.keys()))
    with kpi_col2:
        top_n_worst = st.number_input("🔢 Nhập số lượng Worst Cells (N):", min_value=1, max_value=200, value=10, step=1)

    target_col, sort_ascending = available_kpi_options[sel_worst_kpi_lbl]

    agg_dict = {
        col: ("sum" if col == "TRAFFIC" else "mean") 
        for col in [
            "SGNB_ADD_SUCCESS_RATE", "SGNB_ABN_RELEASE_RATE",
            "INTRA_SGNB_PS_CHANGE", "INTER_SGNB_PS_CHANGE",
            "USER_DL_AVG_THROUGHPUT", "USER_UL_AVG_THROUGHPUT",
            "CQI_5G", "DLINK_RES_BLK_ULT", "ULINK_RES_BLK_ULT", "TRAFFIC"
        ] if col in filtered_df.columns
    }
    cell_agg = filtered_df.groupby([site_col, cell_col]).agg(agg_dict).reset_index()

    res_df = cell_agg.sort_values(by=target_col, ascending=sort_ascending).head(int(top_n_worst))

    st.markdown(f"**Danh sách Top {top_n_worst} Worst Cells theo `{sel_worst_kpi_lbl}`:**")
    st.dataframe(res_df, use_container_width=True)

    worst10_add_sr = cell_agg.sort_values(by="SGNB_ADD_SUCCESS_RATE", ascending=True).head(10) if "SGNB_ADD_SUCCESS_RATE" in cell_agg.columns else pd.DataFrame()
    worst10_drop = cell_agg.sort_values(by="SGNB_ABN_RELEASE_RATE", ascending=False).head(10) if "SGNB_ABN_RELEASE_RATE" in cell_agg.columns else pd.DataFrame()
    worst10_intra_ho = cell_agg.sort_values(by="INTRA_SGNB_PS_CHANGE", ascending=True).head(10) if "INTRA_SGNB_PS_CHANGE" in cell_agg.columns else pd.DataFrame()
    worst10_inter_ho = cell_agg.sort_values(by="INTER_SGNB_PS_CHANGE", ascending=True).head(10) if "INTER_SGNB_PS_CHANGE" in cell_agg.columns else pd.DataFrame()

    return worst10_add_sr, worst10_drop, worst10_intra_ho, worst10_inter_ho

def render_pdf_export_section(filtered_df, site_col, cell_col, top_site_df, top_cell_df, worst10_add_sr, worst10_drop, worst10_intra_ho, worst10_inter_ho, has_hour_info):
    st.subheader("📄 PDF Report Export")

    # Nút Tạo Báo Cáo PDF
    generate_btn = st.button("📄 Tạo Báo Cáo PDF", key="btn_gen_pdf")

    if generate_btn:
        with st.spinner("⏳ Đang tính toán và khởi tạo Báo cáo PDF 5G..."):
            top10_sites_pdf = top_site_df.head(10) if not top_site_df.empty else pd.DataFrame()
            top10_cells_pdf = top_cell_df.head(10) if not top_cell_df.empty else pd.DataFrame()

            fb_cell_counts, fb_tf_df = pd.DataFrame(), pd.DataFrame()
            if cell_col and "Freqband" in filtered_df.columns:
                cell_fb_df = filtered_df[[cell_col, "Freqband"]].drop_duplicates()
                fb_cell_counts = cell_fb_df["Freqband"].value_counts().reset_index()
                fb_cell_counts.columns = ["Freqband", "Số lượng Cell"]
                fb_cell_counts = fb_cell_counts.sort_values(by="Freqband")

                if "TRAFFIC" in filtered_df.columns:
                    fb_tf_df = filtered_df.groupby("Freqband")["TRAFFIC"].sum().reset_index()
                    fb_tf_df = fb_tf_df.sort_values(by="Freqband")

            s_tf = filtered_df.get("TRAFFIC", pd.Series([0]))
            s_intra = filtered_df.get("INTRA_SGNB_PS_CHANGE", pd.Series([0]))
            s_inter = filtered_df.get("INTER_SGNB_PS_CHANGE", pd.Series([0]))

            summary_data = {
                "tf": s_tf.sum(),
                "add_sr": calc_weighted_avg(filtered_df, "SGNB_ADD_SUCCESS_RATE"),
                "drop": calc_weighted_avg(filtered_df, "SGNB_ABN_RELEASE_RATE"),
                "dl": calc_weighted_avg(filtered_df, "USER_DL_AVG_THROUGHPUT"),
                "ul": calc_weighted_avg(filtered_df, "USER_UL_AVG_THROUGHPUT"),
                "cqi": calc_weighted_avg(filtered_df, "CQI_5G"),
                "prb_dl": calc_weighted_avg(filtered_df, "DLINK_RES_BLK_ULT"),
                "prb_ul": calc_weighted_avg(filtered_df, "ULINK_RES_BLK_ULT"),
                "intra": s_intra.mean(),
                "inter": s_inter.mean(),
            }

            if has_hour_info and "DateTime" in filtered_df.columns:
                c_data_timeline = filtered_df.groupby(["Date", "Hour", "DateTime"]).apply(
                    lambda g: pd.Series({
                        "TRAFFIC": g["TRAFFIC"].sum() if "TRAFFIC" in g else 0,
                        "USER_DL_AVG_THROUGHPUT": calc_weighted_avg(g, "USER_DL_AVG_THROUGHPUT"),
                        "USER_UL_AVG_THROUGHPUT": calc_weighted_avg(g, "USER_UL_AVG_THROUGHPUT"),
                        "SGNB_ABN_RELEASE_RATE": calc_weighted_avg(g, "SGNB_ABN_RELEASE_RATE"),
                        "SGNB_ADD_SUCCESS_RATE": calc_weighted_avg(g, "SGNB_ADD_SUCCESS_RATE"),
                        "INTRA_SGNB_PS_CHANGE": g["INTRA_SGNB_PS_CHANGE"].mean() if "INTRA_SGNB_PS_CHANGE" in g else 0,
                        "INTER_SGNB_PS_CHANGE": g["INTER_SGNB_PS_CHANGE"].mean() if "INTER_SGNB_PS_CHANGE" in g else 0,
                        "DLINK_RES_BLK_ULT": calc_weighted_avg(g, "DLINK_RES_BLK_ULT")
                    })
                ).reset_index().sort_values(by="DateTime")
                c_data_timeline["TimeLabel"] = c_data_timeline["DateTime"].dt.strftime("%d/%m %H:00")
            else:
                c_data_timeline = filtered_df.groupby("Date").apply(
                    lambda g: pd.Series({
                        "TRAFFIC": g["TRAFFIC"].sum() if "TRAFFIC" in g else 0,
                        "USER_DL_AVG_THROUGHPUT": calc_weighted_avg(g, "USER_DL_AVG_THROUGHPUT"),
                        "USER_UL_AVG_THROUGHPUT": calc_weighted_avg(g, "USER_UL_AVG_THROUGHPUT"),
                        "SGNB_ABN_RELEASE_RATE": calc_weighted_avg(g, "SGNB_ABN_RELEASE_RATE"),
                        "SGNB_ADD_SUCCESS_RATE": calc_weighted_avg(g, "SGNB_ADD_SUCCESS_RATE"),
                        "INTRA_SGNB_PS_CHANGE": g["INTRA_SGNB_PS_CHANGE"].mean() if "INTRA_SGNB_PS_CHANGE" in g else 0,
                        "INTER_SGNB_PS_CHANGE": g["INTER_SGNB_PS_CHANGE"].mean() if "INTER_SGNB_PS_CHANGE" in g else 0,
                        "DLINK_RES_BLK_ULT": calc_weighted_avg(g, "DLINK_RES_BLK_ULT")
                    })
                ).reset_index().sort_values(by="Date")
                c_data_timeline["TimeLabel"] = pd.to_datetime(c_data_timeline["Date"]).dt.strftime("%d/%m/%Y")

            pdf_buf = generate_pdf_report(
                summary_data,
                c_data_timeline,
                top10_sites_pdf,
                top10_cells_pdf,
                worst10_add_sr,
                worst10_drop,
                worst10_intra_ho,
                worst10_inter_ho,
                fb_cell_counts,
                fb_tf_df
            )
            st.session_state["pdf_bytes"] = pdf_buf.getvalue()

    # Nút Tải Báo Cáo PDF hiển thị phía dưới nút Tạo
    if "pdf_bytes" in st.session_state:
        st.download_button(
            label="⬇️ Tải Báo Cáo PDF",
            data=st.session_state["pdf_bytes"],
            file_name="5G_Network_Health.pdf",
            mime="application/pdf",
            key="btn_dl_pdf"
        )

    st.caption("🚀 5G RAN Quality Report")
