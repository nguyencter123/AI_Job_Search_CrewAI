# File: views/profile_setup_ui.py
import streamlit as st

from services.user_service import update_profile, upload_avatar
from views.utils import load_css

def render_profile_setup():
    load_css("assets/style.css")
    
    st.markdown("<h1 style='text-align: center;'>🎯 Hoàn thiện Hồ sơ Năng lực</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Để AI hỗ trợ bạn tốt nhất, hãy chia sẻ một chút về năng lực của bạn nhé.</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True): 
            # --- ẢNH ĐẠI DIỆN ---
            st.markdown("### 📷 Ảnh đại diện")
            avatar_file = st.file_uploader(
                "Tải ảnh lên (bắt buộc)",
                type=["jpg", "jpeg", "png"],
                help="Chỉ chấp nhận file .jpg hoặc .png, tối đa 2MB.",
            )
            if avatar_file:
                st.image(avatar_file, caption="Xem trước ảnh đại diện", width=150)

            st.divider()

            # --- THÔNG TIN CHUYÊN MÔN ---
            st.markdown("### Thông tin chuyên môn")
            skills = st.text_area("Kỹ năng của bạn", placeholder="Ví dụ: Python, Streamlit, MySQL, Kỹ năng giao tiếp...", help="Liệt kê các công nghệ hoặc kỹ năng bạn thông thạo.")
            experience = st.text_area("Tóm tắt kinh nghiệm", placeholder="Ví dụ: Sinh viên năm cuối, có kinh nghiệm làm dự án đồ án...", height=150)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Lưu và Vào Trang chủ 🚀", type="primary", use_container_width=True):
                if not avatar_file:
                    st.warning("📷 Vui lòng tải ảnh đại diện lên!")
                elif not skills or not experience:
                    st.warning("Vui lòng điền đầy đủ thông tin để AI có thể phân tích chính xác!")
                else:
                    # Lưu ảnh đại diện
                    avatar_bytes = avatar_file.getvalue()
                    avatar_ok, avatar_err = upload_avatar(
                        st.session_state["user_id"], avatar_bytes, avatar_file.type
                    )
                    if not avatar_ok:
                        st.error(avatar_err)
                        return

                    # Lưu kỹ năng & kinh nghiệm
                    success, error = update_profile(st.session_state["user_id"], skills, experience)
                    if success:
                        st.success("Đang chuyển hướng...")
                        st.rerun()
                    else:
                        st.error(error)