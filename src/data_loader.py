import os
import pandas as pd
import streamlit as st

def parse_gio(series):
    if pd.api.types.is_numeric_dtype(series):
        if series.max() <= 1.0 and series.min() >= 0.0:
            return (series * 24).round().astype("Int64")
        else:
            return series.round().astype("Int64")
    
    s_str = series.astype(str).str.strip()
    s_num = pd.to_numeric(s_str, errors="coerce")
    if s_num.notnull().all():
        if s_num.max() <= 1.0 and s_num.min() >= 0.0:
            return (s_num * 24).round().astype("Int64")
        else:
            return s_num.round().astype("Int64")
    
    parsed = pd.to_datetime(s_str, format="%H:%M:%S", errors="coerce")
    if parsed.isna().all():
        parsed = pd.to_datetime(s_str, format="%I:%M:%S %p", errors="coerce")
    if parsed.isna().all():
        parsed = pd.to_datetime(s_str, format="%H:%M", errors="coerce")
    if parsed.isna().all():
        parsed = pd.to_datetime(s_str, errors="coerce")
        
    return parsed.dt.hour.astype("Int64")

@st.cache_data
def process_data(file_input):
    # 1. Bắt lỗi không đọc được file CSV
    try:
        df = pd.read_csv(file_input)
    except Exception as e:
        st.error(f"❌ Không thể đọc file CSV! Kiểm tra định dạng hoặc mã hóa file. (Lỗi: {e})")
        return None

    # 2. Bắt lỗi file rỗng
    if df is None or df.empty:
        st.error("❌ File CSV không chứa dữ liệu (file rỗng)!")
        return None

    # 3. Kiểm tra xem có đúng là file KPI 5G hay không
    kpi_indicators = [
        "SGNB_ADD_SUCCESS_RATE", "SGNB_ABN_RELEASE_RATE", 
        "USER_DL_AVG_THROUGHPUT", "CQI_5G", "TRAFFIC", 
        "DL_TRAFFIC_VOLUME", "INTRA_SGNB_PS_CHANGE"
    ]
    # File hợp lệ nếu chứa ít nhất 2 cột KPI đặc trưng của 5G
    found_kpis = [col for col in kpi_indicators if col in df.columns]
    if len(found_kpis) < 2:
        st.error("⚠️ File tải lên không đúng định dạng KPI 5G! Vui lòng kiểm tra lại cấu hình cột trong file CSV.")
        return None

    # --- Phần xử lý dữ liệu phía dưới giữ nguyên ---
    site_cols = ["Tên GNODEB", "gNodeB Name", "gNODEB Name", "Site Name"]
    cell_cols = ["Tên CELL", "Cell Name", "CELL Name"]

    site_col = next((c for c in site_cols if c in df.columns), None)
    cell_col = next((c for c in cell_cols if c in df.columns), None)

    if site_col and site_col != "Tên GNODEB":
        df["Tên GNODEB"] = df[site_col]
    if cell_col and cell_col != "Tên CELL":
        df["Tên CELL"] = df[cell_col]

    date_cols = ["Ngày", "Thời gian", "Date", "DATE", "ngay", "thoi_gian"]
    date_col = next((c for c in date_cols if c in df.columns), None)
    
    if date_col:
        s_date = df[date_col]
        if pd.api.types.is_numeric_dtype(s_date) and (s_date > 30000).any():
            df["Date"] = pd.to_datetime(s_date, unit="D", origin="1899-12-30").dt.date
        else:
            df["Date"] = pd.to_datetime(s_date, dayfirst=True, errors="coerce").dt.date
    else:
        df["Date"] = pd.Timestamp.now().date()

    if "Giờ" in df.columns:
        df["Hour"] = parse_gio(df["Giờ"])
    elif "Hour" in df.columns:
        df["Hour"] = parse_gio(df["Hour"])

    if "Date" in df.columns and "Hour" in df.columns and df["Hour"].notnull().any():
        valid_mask = df["Hour"].notnull() & df["Date"].notnull()
        df.loc[valid_mask, "DateTime"] = pd.to_datetime(
            df.loc[valid_mask, "Date"].astype(str) + " " + df.loc[valid_mask, "Hour"].astype(int).astype(str) + ":00:00",
            errors="coerce"
        )

    if "Tên CELL" in df.columns:
        def extract_freqband(cell_name):
            s = str(cell_name).strip()
            if len(s) >= 11:
                digit_char = s[10]
                if digit_char.isdigit():
                    return f"F{digit_char}"
                elif digit_char.upper().startswith("F"):
                    return digit_char.upper()
            return "N/A"
        df["Freqband"] = df["Tên CELL"].apply(extract_freqband)
    else:
        df["Freqband"] = "N/A"

    kpi_cols = [
        "USER_UL_AVG_THROUGHPUT", "CQI_5G", "INTRA_SGNB_PS_CHANGE",
        "DLINK_RES_BLK_ULT", "ULINK_RES_BLK_ULT", "UL_TRAFFIC_VOLUME",
        "DL_TRAFFIC_VOLUME", "SGNB_ABN_RELEASE_RATE", "SGNB_ADD_SUCCESS_RATE",
        "USER_DL_AVG_THROUGHPUT", "TRAFFIC", "INTER_SGNB_PS_CHANGE"
    ]

    for col in kpi_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "TRAFFIC" not in df.columns:
        if "DL_TRAFFIC_VOLUME" in df.columns and "UL_TRAFFIC_VOLUME" in df.columns:
            df["TRAFFIC"] = df["DL_TRAFFIC_VOLUME"].fillna(0) + df["UL_TRAFFIC_VOLUME"].fillna(0)
        elif "DL_TRAFFIC_VOLUME" in df.columns:
            df["TRAFFIC"] = df["DL_TRAFFIC_VOLUME"]
        else:
            df["TRAFFIC"] = 0.0

    return df

def calc_weighted_avg(df_in, kpi_col, weight_col="TRAFFIC"):
    if kpi_col not in df_in.columns:
        return 0.0
    
    valid_mask = df_in[kpi_col].notnull()
    if weight_col in df_in.columns:
        valid_mask = valid_mask & df_in[weight_col].notnull()
        df_valid = df_in[valid_mask]
        total_weight = df_valid[weight_col].sum()
        if total_weight > 0:
            return (df_valid[kpi_col] * df_valid[weight_col]).sum() / total_weight

    df_valid = df_in[df_in[kpi_col].notnull()]
    return df_valid[kpi_col].mean() if not df_valid.empty else 0.0
