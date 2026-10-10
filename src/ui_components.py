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
