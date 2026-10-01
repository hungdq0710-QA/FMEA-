import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="FMEA & C&E Matrix - Probe Card Dashboard", layout="wide")

st.title("🛡️ Quality Management Dashboard - Probe Card")
st.markdown("Hệ thống quản lý rủi ro **FMEA** & **C&E Matrix** phối hợp giữa **QA** và **Production** (Dữ liệu được lưu tự động vĩnh viễn trên máy).")

# --- QUẢN LÝ LƯU TRỮ FILE CỐ ĐỊNH TRÊN MÁY ---
FMEA_FILE = "fmea_data.csv"
CE_FILE = "ce_data.csv"

# 1. Khởi tạo dữ liệu FMEA
if not os.path.exists(FMEA_FILE):
    default_fmea = pd.DataFrame([
        {
            "Công đoạn": "Kiểm tra & Chuẩn bị PCB",
            "Tiềm ẩn lỗi": "Lỗi mạch (Open/Short)",
            "Tác động (SEV)": 8,
            "Nguyên nhân": "Lỗi file Gerber hoặc mòn mũi khoan",
            "Giải pháp kiểm soát": "Tự động hóa kiểm tra AOI",
            "Phòng ban": "Production",
            "Trạng thái": "Đang xử lý",
            "DET": 4
        },
        {
            "Công đoạn": "Gắn Spider Springs",
            "Tiềm ẩn lỗi": "Lực ép spring không đều",
            "Tác động (SEV)": 9,
            "Nguyên nhân": "Thao tác thủ công hoặc jig mòn",
            "Giải pháp kiểm soát": "Cải tiến jig định vị tự động",
            "Phòng ban": "QA",
            "Trạng thái": "Hoàn thành",
            "DET": 3
        }
    ])
    default_fmea.to_csv(FMEA_FILE, index=False)

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

# Đọc dữ liệu từ file lên app
df_fmea = pd.read_csv(FMEA_FILE)
df_ce = pd.read_csv(CE_FILE)

# --- SIDEBAR MENU ---
st.sidebar.header("⚙️ Điều hướng hệ thống")
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
    df_fmea["RPN"] = df_fmea["Tác động (SEV)"] * df_fmea["DET"]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng số lỗi tiềm ẩn", len(df_fmea))
    col2.metric("Lỗi RPN Cao (>150)", len(df_fmea[df_fmea["RPN"] > 150]))
    col3.metric("Đã hoàn thành cải tiến", len(df_fmea[df_fmea["Trạng thái"] == "Hoàn thành"]))
    
    st.markdown("---")
    st.dataframe(df_fmea, use_container_width=True)

# --- 2. QUẢN LÝ & CẬP NHẬT FMEA ---
elif menu == "✏️ Quản lý & Cập nhật FMEA":
    st.subheader("✏️ Cập nhật trạng thái và thông số FMEA")
    
    edited_df = st.data_editor(df_fmea, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Lưu thay đổi FMEA vào hệ thống"):
        edited_df.to_csv(FMEA_FILE, index=False)
        st.success("Đã lưu thay đổi vào file hệ thống thành công! Dữ liệu sẽ được giữ nguyên khi bạn tắt/mở lại.")
        st.rerun()

# --- 3. THÊM LỖI FMEA ---
elif menu == "➕ Thêm lỗi FMEA":
    st.subheader("➕ Thêm hạng mục lỗi vào bảng FMEA")
    
    with st.form("new_fmea_form"):
        col1, col2 = st.columns(2)
        with col1:
            cong_doan = st.selectbox("Công đoạn sản xuất", ["Kiểm tra & Chuẩn bị PCB", "Gắn Spider Springs", "Electrical & Alignment Test", "QA Final Inspection"])
            loi = st.text_input("Tiềm ẩn lỗi (Failure Mode)")
            sev = st.slider("Mức độ nghiêm trọng (SEV: 1-10)", 1, 10, 5)
            det = st.slider("Khả năng phát hiện (DET: 1-10)", 1, 10, 5)
        with col2:
            nguyen_nhan = st.text_area("Nguyên nhân gốc rễ")
            giai_phap = st.text_area("Giải pháp kiểm soát")
            phong_ban = st.selectbox("Bộ phận chịu trách nhiệm", ["Production", "QA"])
            trang_thai = st.selectbox("Trạng thái", ["Chưa bắt đầu", "Đang xử lý", "Hoàn thành"])
        
        submitted = st.form_submit_button("Thêm vào hệ thống")
        if submitted:
            if loi:
                new_row = {
                    "Công đoạn": cong_doan,
                    "Tiềm ẩn lỗi": loi,
                    "Tác động (SEV)": sev,
                    "Nguyên nhân": nguyen_nhan,
                    "Giải pháp kiểm soát": giai_phap,
                    "Phòng ban": phong_ban,
                    "Trạng thái": trang_thai,
                    "DET": det
                }
                updated_fmea = pd.concat([df_fmea, pd.DataFrame([new_row])], ignore_index=True)
                updated_fmea.to_csv(FMEA_FILE, index=False)
                st.success("Đã thêm và lưu vĩnh viễn vào hệ thống thành công!")
                st.rerun()
            else:
                st.warning("Vui lòng nhập tên tiềm ẩn lỗi.")

# --- 4. C&E MATRIX (CAUSE & EFFECT MATRIX) ---
elif menu == "🎯 C&E Matrix (Cause & Effect)":
    st.subheader("🎯 Cause & Effect Matrix: *“Process/Input nào có ảnh hưởng lớn đến Quality Output nào?”*")
    st.markdown("Nhập thông tin quy trình, đầu vào, giải thích chi tiết và chấm điểm mức độ ảnh hưởng.")
    
    with st.form("ce_matrix_form"):
        st.markdown("### 📝 1. Thêm mới Process, Input & Giải thích chi tiết")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            process_input = st.text_input("Process (Quy trình sản xuất)", placeholder="Ví dụ: Gắn Spider Springs")
            input_input = st.text_input("Input (Yếu tố đầu vào / Biến số)", placeholder="Ví dụ: Lực ép jig")
        with col_p2:
            giai_thich_input = st.text_area("🔍 Giải thích lỗi / Mô tả chi tiết về Input", placeholder="Mô tả rõ Input này là gì...")
            
        st.markdown("### 🎚️ 2. Chấm điểm mức độ ảnh hưởng đến các Output (Sliders: 0 - 10)")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            probe_mark = st.slider("Probe Mark", 0, 10, 5)
            function = st.slider("Function", 0, 10, 5)
            leakage_short = st.slider("Leakage/Short", 0, 10, 5)
            cosmetic = st.slider("Cosmetic", 0, 10, 5)
        with col_s2:
            iqc_pa = st.slider("IQC P&A", 0, 10, 5)
            mechanical_robust = st.slider("Mechanical Robust", 0, 10, 5)
            contact_open = st.slider("Contact/Open", 0, 10, 5)
            packing = st.slider("Packing", 0, 10, 5)
        with col_s3:
            delivery = st.slider("Delivery", 0, 10, 5)
            life_time = st.slider("Life Time", 0, 10, 5)
            rma = st.slider("RMA", 0, 10, 5)
            
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
                updated_ce = pd.concat([df_ce, pd.DataFrame([new_ce_row])], ignore_index=True)
                updated_ce.to_csv(CE_FILE, index=False)
                st.success("Đã thêm thành công vào C&E Matrix!")
                st.rerun()
            else:
                st.warning("Vui lòng điền đầy đủ tên Process và Input.")

    st.markdown("---")
    st.subheader("📋 Quản lý & Chỉnh sửa / Xóa dòng trong C&E Matrix")
    st.info("💡 **Mẹo xóa dòng:** Bạn có thể bấm chọn vào ô vuông ở đầu dòng cần xóa trong bảng dưới đây rồi bấm phím **Delete** trên bàn phím, hoặc bấm vào biểu tượng thùng rác xuất hiện khi chọn dòng, sau đó bấm nút **💾 Lưu thay đổi**.")
    
    # Cho phép chỉnh sửa trực tiếp hoặc xóa dòng
    edited_ce_df = st.data_editor(df_ce.sort_values(by="Tổng điểm", ascending=False), use_container_width=True, num_rows="dynamic", key="ce_editor")
    
    if st.button("💾 Lưu thay đổi (Cập nhật / Xóa dòng)"):
        edited_ce_df.to_csv(CE_FILE, index=False)
        st.success("Đã cập nhật và lưu lại danh sách C&E Matrix thành công!")
        st.rerun()
# --- 5. TÀI LIỆU GIỚI THIỆU FMEA & LỖI ---
elif menu == "📖 Tài liệu giới thiệu FMEA & Lỗi":
    st.subheader("📚 Tài liệu hướng dẫn & Giải thích lỗi trong sản xuất Probe Card")
    st.markdown("""
    ### 1. Bản chất của FMEA
    * **FMEA = Failure Mode and Effects Analysis**: Phân tích quy trình/sản phẩm để dự đoán rủi ro và phòng ngừa trước[cite: 1].
    
    ### 2. Các chỉ số rủi ro:
    * **RPN = S × O × D**: Chỉ số ưu tiên rủi ro.
    
    ### 3. Giải thích Quality Outputs:
    * **Probe Mark, Function, Leakage/Short, Cosmetic, IQC P&A, Mechanical Robust, Contact/Open, Packing, Delivery, Life Time, RMA.**
    """)