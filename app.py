import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="FMEA & C&E Matrix - Probe Card Dashboard", layout="wide")

st.title("🛡️ Quality Management Dashboard - Probe Card")
st.markdown("Hệ thống quản lý rủi ro **FMEA** & **C&E Matrix** phối hợp giữa **QA** và **Production** (Dữ liệu được lưu tự động vĩnh viễn trên máy/Cloud).")

# --- QUẢN LÝ LƯU TRỮ FILE CỐ ĐỊNH ---
FMEA_FILE = "fmea_data.csv"
CE_FILE = "ce_data.csv"

# Chuẩn hóa danh sách cột FMEA đầy đủ
fmea_cols = [
    "Công đoạn", "Potential Failure Mode", "Potential Effect (Local)", 
    "Potential Effect (Customer)", "Nguyên nhân", "Giải pháp", 
    "Bộ phận", "Trạng thái", "Severity (S)", "Occurrence (O)", "Detection (D)", "RPN"
]

# 1. Khởi tạo hoặc đọc dữ liệu FMEA an toàn
if os.path.exists(FMEA_FILE):
    try:
        df_fmea = pd.read_csv(FMEA_FILE)
        for col in fmea_cols:
            if col not in df_fmea.columns:
                df_fmea[col] = 5 if "S" in col or "O" in col or "D" in col or "RPN" in col else ""
    except Exception:
        df_fmea = pd.DataFrame(columns=fmea_cols)
else:
    df_fmea = pd.DataFrame([
        {
            "Công đoạn": "IQA-QA",
            "Potential Failure Mode": "Lỗi mạch (Open/Short)",
            "Potential Effect (Local)": "Mạch hở tại chân tiếp xúc",
            "Potential Effect (Customer)": "Không test được wafer",
            "Nguyên nhân": "Lỗi file Gerber hoặc mòn mũi khoan",
            "Giải pháp": "Tự động hóa kiểm tra AOI",
            "Bộ phận": "Production",
            "Trạng thái": "In Progress",
            "Severity (S)": 8,
            "Occurrence (O)": 5,
            "Detection (D)": 4,
            "RPN": 160
        }
    ], columns=fmea_cols)
    df_fmea.to_csv(FMEA_FILE, index=False)

# 2. Khởi tạo dữ liệu C&E Matrix
if not os.path.exists(CE_FILE):
    default_ce = pd.DataFrame([
        {
            "Process": "Lắp ráp Spider Springs",
            "Input": "Độ chính xác lực ép jig",
            "Giải thích Input": "Lực tác động của jig khi ép spider springs lên PCB, lực không đều gây biến dạng.",
            "Probe Mark": 9,
            "Function": 8,
            "Leakage/Short": 3,
            "Cosmetic": 2,
            "IQC P&A": 4,
            "Mechanical Robust": 9,
            "Contact/Open": 9,
            "Packing": 1,
            "Delivery": 1,
            "Life Time": 8,
            "RMA": 7,
            "Tổng điểm": 61
        }
    ])
    default_ce.to_csv(CE_FILE, index=False)

df_ce = pd.read_csv(CE_FILE)

# --- SIDEBAR MENU GIỮ NGUYÊN ĐẦY ĐỦ CÁC MỤC ---
st.sidebar.header("⚙ Điều hướng hệ thống")
menu = st.sidebar.selectbox("Chọn chức năng", [
    "📊 Tổng quan FMEA", 
    "✏️ Quản lý & Cập nhật FMEA", 
    "➕ Thêm lỗi FMEA",
    "🎯 C&E Matrix (Cause & Effect)",
    "📖 Tài liệu giới thiệu FMEA & Lỗi"
])

# --- 1. TỔNG QUAN FMEA ---
if menu == "📊 Tổng quan FMEA":
    st.subheader("📊 Chỉ số rủi ro FMEA tổng quan")
    
    df_fmea["Severity (S)"] = pd.to_numeric(df_fmea["Severity (S)"], errors='coerce').fillna(1)
    df_fmea["Occurrence (O)"] = pd.to_numeric(df_fmea["Occurrence (O)"], errors='coerce').fillna(1)
    df_fmea["Detection (D)"] = pd.to_numeric(df_fmea["Detection (D)"], errors='coerce').fillna(1)
    df_fmea["RPN"] = df_fmea["Severity (S)"] * df_fmea["Occurrence (O)"] * df_fmea["Detection (D)"]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng số lỗi tiềm ẩn", len(df_fmea))
    col2.metric("Lỗi RPN Cao (>150)", len(df_fmea[df_fmea["RPN"] > 150]))
    col3.metric("Đã hoàn thành cải tiến", len(df_fmea[df_fmea["Trạng thái"] == "Closed"]))
    
    st.markdown("---")
    st.dataframe(df_fmea, use_container_width=True)

# --- 2. QUẢN LÝ & CẬP NHẬT FMEA (ĐÃ ĐỔI THÀNH DẠNG BẢNG TABLE TƯƠNG TÁC) ---
elif menu == "✏️ Quản lý & Cập nhật FMEA":
    st.subheader("✏️ Quản lý, Chỉnh sửa, Thêm & Xóa trực tiếp trên bảng FMEA")
    st.info("💡 **Hướng dẫn:** Bạn có thể chỉnh sửa trực tiếp nội dung trên các ô, thêm dòng mới bằng dấu cộng ở cuối bảng, hoặc chọn xóa dòng. Sau khi chỉnh sửa xong, hãy bấm nút **💾 Lưu thay đổi** ở bên dưới.")
    
    # Tính toán lại RPN trước khi hiển thị
    df_fmea["Severity (S)"] = pd.to_numeric(df_fmea["Severity (S)"], errors='coerce').fillna(1)
    df_fmea["Occurrence (O)"] = pd.to_numeric(df_fmea["Occurrence (O)"], errors='coerce').fillna(1)
    df_fmea["Detection (D)"] = pd.to_numeric(df_fmea["Detection (D)"], errors='coerce').fillna(1)
    df_fmea["RPN"] = df_fmea["Severity (S)"] * df_fmea["Occurrence (O)"] * df_fmea["Detection (D)"]
    
    df_fmea_sorted = df_fmea.sort_values(by="RPN", ascending=False)
    
    edited_fmea_df = st.data_editor(
        df_fmea_sorted, 
        use_container_width=True, 
        num_rows="dynamic", 
        key="fmea_grid_editor",
        column_config={
            "Severity (S)": st.column_config.NumberColumn("Severity (S)", min_value=1, max_value=10, step=1),
            "Occurrence (O)": st.column_config.NumberColumn("Occurrence (O)", min_value=1, max_value=10, step=1),
            "Detection (D)": st.column_config.NumberColumn("Detection (D)", min_value=1, max_value=10, step=1),
            "RPN": st.column_config.NumberColumn("RPN (Tự động)", disabled=True),
            "Trạng thái": st.column_config.SelectboxColumn("Trạng thái", options=["Open", "In Progress", "Closed"], required=True),
            "Công đoạn": st.column_config.SelectboxColumn("Công đoạn", options=["IQA-QA", "REFLOW", "SPACE TRANSFOMER", "VQA-QA", "PCA-QA", "OQA-QA", "PACKING-QA"], required=True)
        }
    )
    
    if st.button("💾 Lưu thay đổi FMEA", type="primary"):
        edited_fmea_df["Severity (S)"] = pd.to_numeric(edited_fmea_df["Severity (S)"], errors='coerce').fillna(1)
        edited_fmea_df["Occurrence (O)"] = pd.to_numeric(edited_fmea_df["Occurrence (O)"], errors='coerce').fillna(1)
        edited_fmea_df["Detection (D)"] = pd.to_numeric(edited_fmea_df["Detection (D)"], errors='coerce').fillna(1)
        edited_fmea_df["RPN"] = edited_fmea_df["Severity (S)"] * edited_fmea_df["Occurrence (O)"] * edited_fmea_df["Detection (D)"]
        
        edited_fmea_df.to_csv(FMEA_FILE, index=False)
        st.success("Đã lưu lại toàn bộ thay đổi và cập nhật chỉ số RPN thành công!")
        st.rerun()

# --- 3. THÊM MỚI LỖI FMEA ---
elif menu == "➕ Thêm lỗi FMEA":
    st.subheader("➕ Thêm mới lỗi FMEA cho quy trình sản xuất Probe Card")
    
    with st.form("fmea_form"):
        st.markdown("### 📝 Thông tin chi tiết lỗi FMEA")
        
        cong_doan = st.selectbox(
            "Công đoạn sản xuất", 
            ["IQA-QA", "REFLOW", "SPACE TRANSFOMER", "VQA-QA", "PCA-QA", "OQA-QA", "PACKING-QA"]
        )
        
        potential_failure_mode = st.text_input("Potential Failure Mode (Dạng lỗi tiềm ẩn)", placeholder="Ví dụ: Lỗi hàn không đều...")
        potential_effect_local = st.text_area("Potential Effect – Local / Next Process", placeholder="Mô tả ảnh hưởng trực tiếp...")
        potential_effect_customer = st.text_area("Potential Effect – Product / Customer", placeholder="Mô tả ảnh hưởng cuối cùng...")
        
        nguyen_nhan = st.text_area("Nguyên nhân gốc rễ (Potential Causes)", placeholder="Nguyên nhân gây ra lỗi...")
        giai_phap = st.text_area("Giải pháp kiểm soát / Hành động cải tiến", placeholder="Biện pháp phòng ngừa...")
        
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            bo_phan = st.text_input("Bộ phận chịu trách nhiệm (Responsible)", placeholder="QA, Production...")
        with col_meta2:
            trang_thai = st.selectbox("Trạng thái (Status)", ["Open", "In Progress", "Closed"])
        
        st.markdown("### 🎚️ Đánh giá rủi ro (Risk Evaluation)")
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            severity = st.slider("Severity (S)", 1, 10, 5)
        with col_s2:
            occurrence = st.slider("Occurrence (O)", 1, 10, 5)
        with col_s3:
            detection = st.slider("Detection (D)", 1, 10, 5)
            
        rpn = severity * occurrence * detection
        st.info(f"⚡ **Chỉ số RPN tính toán tự động:** S × O × D = {severity} × {occurrence} × {detection} = **{rpn}**")
        
        submitted_fmea = st.form_submit_button("💾 Lưu lỗi FMEA vào hệ thống")
        
        if submitted_fmea:
            if potential_failure_mode:
                new_fmea_row = {
                    "Công đoạn": cong_doan,
                    "Potential Failure Mode": potential_failure_mode,
                    "Potential Effect (Local)": potential_effect_local,
                    "Potential Effect (Customer)": potential_effect_customer,
                    "Nguyên nhân": nguyen_nhan,
                    "Giải pháp": giai_phap,
                    "Bộ phận": bo_phan,
                    "Trạng thái": trang_thai,
                    "Severity (S)": severity,
                    "Occurrence (O)": occurrence,
                    "Detection (D)": detection,
                    "RPN": rpn
                }
                updated_fmea = pd.concat([df_fmea, pd.DataFrame([new_fmea_row])], ignore_index=True)
                updated_fmea.to_csv(FMEA_FILE, index=False)
                st.success("Đã thêm lỗi FMEA mới thành công!")
                st.rerun()
            else:
                st.warning("Vui lòng điền thông tin 'Potential Failure Mode'.")

# --- 4. C&E MATRIX ---
elif menu == "🎯 C&E Matrix (Cause & Effect)":
    st.subheader("🎯 Cause & Effect Matrix: *“Process/Input nào có ảnh hưởng lớn đến Quality Output nào?”*")
    st.markdown("Nhập thông tin quy trình, đầu vào, giải thích chi tiết và chấm điểm mức độ ảnh hưởng.")
    
    with st.form("ce_matrix_form", clear_on_submit=True):
        st.markdown("### 📝 1. Thêm mới Process, Input & Giải thích chi tiết")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            process_input = st.text_input("Process (Quy trình sản xuất)", placeholder="Ví dụ: Lắp ráp Spider Springs")
            input_input = st.text_input("Input (Yếu tố đầu vào / Biến số)", placeholder="Ví dụ: Lực ép jig")
        with col_p2:
            giai_thich_input = st.text_area("🔍 Giải thích lỗi / Mô tả chi tiết về Input", placeholder="Mô tả rõ Input này là gì...")
            
        st.markdown("### 🎚️ 2. Chấm điểm mức độ ảnh hưởng đến các Output (Sliders: 0 - 10)")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            probe_mark = st.slider("Probe Mark", 0, 10, 5, key="ce_probe")
            function = st.slider("Function", 0, 10, 5, key="ce_func")
            leakage_short = st.slider("Leakage/Short", 0, 10, 5, key="ce_leak")
            cosmetic = st.slider("Cosmetic", 0, 10, 5, key="ce_cos")
        with col_s2:
            iqc_pa = st.slider("IQC P&A", 0, 10, 5, key="ce_iqc")
            mechanical_robust = st.slider("Mechanical Robust", 0, 10, 5, key="ce_mech")
            contact_open = st.slider("Contact/Open", 0, 10, 5, key="ce_cont")
            packing = st.slider("Packing", 0, 10, 5, key="ce_pack")
        with col_s3:
            delivery = st.slider("Delivery", 0, 10, 5, key="ce_deliv")
            life_time = st.slider("Life Time", 0, 10, 5, key="ce_life")
            rma = st.slider("RMA", 0, 10, 5, key="ce_rma")
            
        submitted_ce = st.form_submit_button("➕ Thêm Process/Input vào C&E Matrix")
        
        if submitted_ce:
            if process_input and input_input:
                total_score = (probe_mark + function + leakage_short + cosmetic + 
                               iqc_pa + mechanical_robust + contact_open + packing + 
                               delivery + life_time + rma)
                
                new_ce_row = {
                    "Process": process_input,
                    "Input": input_input,
                    "Giải thích Input": giai_thich_input,
                    "Probe Mark": probe_mark,
                    "Function": function,
                    "Leakage/Short": leakage_short,
                    "Cosmetic": cosmetic,
                    "IQC P&A": iqc_pa,
                    "Mechanical Robust": mechanical_robust,
                    "Contact/Open": contact_open,
                    "Packing": packing,
                    "Delivery": delivery,
                    "Life Time": life_time,
                    "RMA": rma,
                    "Tổng điểm": total_score
                }
                
                # Đọc lại file hiện tại để đảm bảo không bị sót dữ liệu cũ
                if os.path.exists(CE_FILE):
                    current_df_ce = pd.read_csv(CE_FILE)
                else:
                    current_df_ce = df_ce
                
                updated_ce = pd.concat([current_df_ce, pd.DataFrame([new_ce_row])], ignore_index=True)
                updated_ce.to_csv(CE_FILE, index=False)
                st.success("Đã thêm thành công vào C&E Matrix!")
                st.rerun()
            else:
                st.warning("Vui lòng điền đầy đủ tên Process và Input.")

    st.markdown("---")
    st.subheader("📋 Quản lý & Chỉnh sửa / Xóa dòng trong C&E Matrix")
    
    # Đọc lại dữ liệu mới nhất từ file CSV để hiển thị lên bảng bên dưới
    if os.path.exists(CE_FILE):
        df_ce_current = pd.read_csv(CE_FILE)
    else:
        df_ce_current = df_ce

    edited_ce_df = st.data_editor(
        df_ce_current.sort_values(by="Tổng điểm", ascending=False), 
        use_container_width=True, 
        num_rows="dynamic", 
        key="ce_editor"
    )
    
    if st.button("💾 Lưu thay đổi C&E Matrix", key="btn_save_ce"):
        edited_ce_df.to_csv(CE_FILE, index=False)
        st.success("Đã cập nhật và lưu lại danh sách C&E Matrix thành công!")
        st.rerun()

# --- 5. TÀI LIỆU GIỚI THIỆU FMEA & LỖI ---
elif menu == "📖 Tài liệu giới thiệu FMEA & Lỗi":
    st.subheader("📚 Tài liệu hướng dẫn & Giới thiệu FMEA cho Probe Card")
    
    st.markdown("""
    ### 1. Bản chất của FMEA
    * **FMEA = Failure Mode and Effects Analysis**: Phân tích cách một quá trình hoặc sản phẩm có thể xảy ra lỗi, đánh giá hậu quả của lỗi, tìm nguyên nhân gốc rễ và xác định cách kiểm soát/phòng ngừa.
    * **Lưu ý quan trọng**: FMEA **không phải là một danh sách lỗi** thông thường, mà là phương pháp dự đoán trước các rủi ro tiềm ẩn trước khi chúng thực sự xảy ra để chủ động giảm thiểu tác động.
    """)
    
    try:
        st.image("Slide1.png", caption="Sơ đồ tổng quan: FMEA là gì?", width=600)
    except Exception:
        st.warning("⚠️ Chưa tìm thấy file ảnh 'Slide1.png' trên GitHub.")
    
    st.markdown("""
    ### 2. Các chỉ số đánh giá rủi ro trong sản xuất Probe Card:
    """)
    
    try:
        st.image("Slide5.png", caption="Các Chỉ Số", width=600)
    except Exception:
        pass

    st.markdown("""
    * **S (Severity - Mức độ nghiêm trọng):** Ảnh hưởng của lỗi đối với chất lượng test wafer của khách hàng (Thang điểm 1 - 10).
    """)
    
    try:
        st.image("Slide6.png", caption="Severity", width=600)    
    except Exception:
        pass

    st.markdown("""
    * **O (Occurrence – Khả năng xảy ra):** Nguyên nhân này xảy ra thường xuyên đến mức nào? (Thang điểm 1 - 10).
    """)
    
    try:
        st.image("Slide7.png", caption="Occurrence", width=600)    
    except Exception:
        pass

    st.markdown("""
    * **DET (Detection - Khả năng phát hiện):** Khả năng hệ thống kiểm soát và phát hiện ra lỗi trước khi gửi sản phẩm tới cho Customer (Thang điểm 1 - 10).
    """)
    
    try:
        st.image("Slide9.png", caption="Detection", width=600)
    except Exception:
        pass
    
    st.markdown("""
    * **RPN (Risk Priority Number) = S × O × D**: RPN càng cao → cần ưu tiên xử lý càng sớm.
    
    ### 3. Quy trình phối hợp giữa QA & Production:
    * **Production (Sản xuất):** Cập nhật thực trạng kỹ thuật tại xưởng, đưa ra nguyên nhân gốc rễ và tiến độ xử lý.
    * **QA (Chất lượng):** Phối hợp đánh giá mức độ rủi ro, kiểm chứng hiệu quả của các biện pháp kiểm soát và thực hiện nghiệm thu.
    """)