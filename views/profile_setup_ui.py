# File: views/profile_setup_ui.py
import streamlit as st
from repositories.database import SessionLocal
from repositories.user_repo import update_user_profile
from views.utils import load_css

def render_profile_setup():
    load_css("assets/style.css")
    
    st.markdown("<h1 style='text-align: center;'>🎯 Hoàn thiện Hồ sơ Năng lực</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Để AI hỗ trợ bạn tốt nhất, hãy chia sẻ một chút về năng lực của bạn nhé.</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True): 
            st.markdown("### Thông tin chuyên môn")
            skills = st.text_area("Kỹ năng của bạn", placeholder="Ví dụ: Python, Streamlit, MySQL, Kỹ năng giao tiếp...", help="Liệt kê các công nghệ hoặc kỹ năng bạn thông thạo.")
            experience = st.text_area("Tóm tắt kinh nghiệm", placeholder="Ví dụ: Sinh viên năm cuối, có kinh nghiệm làm dự án đồ án...", height=150)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Lưu và Vào Trang chủ 🚀", type="primary", use_container_width=True):
                if not skills or not experience:
                    st.warning("Vui lòng điền đầy đủ thông tin để AI có thể phân tích chính xác!")
                else:
                    db = SessionLocal()
                    try:
                        update_user_profile(db, st.session_state['user_id'], skills, experience)
                        st.success("Đang chuyển hướng...")
                        st.rerun() # Nhấn xong tải lại trang, app.py sẽ đưa vào dashboard
                    finally:
                        db.close()