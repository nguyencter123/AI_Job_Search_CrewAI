# File: views/employer/profile_setup_ui.py
import streamlit as st

from services.user_service import update_employer_info, get_employer_info
from views.utils import load_css

def render_employer_profile_setup():
    load_css("assets/style.css")
    
    st.markdown("<h1 style='text-align: center;'>🏢 Cập nhật Hồ sơ Công ty</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Vui lòng cung cấp thông tin công ty để ứng viên hiểu rõ hơn về nơi làm việc của bạn.</p>", unsafe_allow_html=True)

    uid = st.session_state["user_id"]
    current_info = get_employer_info(uid) or {}

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True): 
            st.markdown("### Thông tin Doanh nghiệp")
            
            company_name = st.text_input("Tên công ty", value=current_info.get("company_name", ""))
            website = st.text_input("Website (Tùy chọn)", value=current_info.get("website", ""))
            address = st.text_input("Địa chỉ trụ sở", value=current_info.get("address", ""))
            
            st.markdown("### Giới thiệu Công ty")
            description = st.text_area(
                "Mô tả về công ty", 
                value=current_info.get("company_description", ""),
                placeholder="Ví dụ: Công ty công nghệ hàng đầu với 10 năm kinh nghiệm...", 
                height=150
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Lưu và Vào Quản lý 🚀", type="primary", use_container_width=True):
                if not company_name or not description or not address:
                    st.warning("⚠️ Vui lòng điền đầy đủ Tên công ty, Mô tả và Địa chỉ!")
                else:
                    success, error = update_employer_info(uid, company_name, description, website, address)
                    if success:
                        st.success("Đang chuyển hướng...")
                        st.rerun()
                    else:
                        st.error(error)
