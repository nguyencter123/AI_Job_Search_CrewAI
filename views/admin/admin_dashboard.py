# File: views/admin/admin_dashboard.py
import streamlit as st
from views.utils import load_css
from views.admin.admin_management import user_management_page

def render_admin_dashboard():
    load_css("assets/style.css")
    
    # --- THANH ĐIỀU HƯỚNG CỦA ADMIN ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #dc2626;'>🛡️ Admin Panel</h2>", unsafe_allow_html=True)
        st.caption("<div style='text-align: center;'>Quyền quản trị tối cao</div>", unsafe_allow_html=True)
        st.divider()
        
        # Menu riêng cho Admin
        admin_menu = st.radio(
            "📍 Quản lý hệ thống",
            ["📊 Thống kê Tổng quan", "👥 Quản lý Người dùng", "💼 Quản lý JD (Công việc)", "⚙️ Cài đặt AI Models"],
            label_visibility="collapsed"
        )
        
        st.spacer = st.container()
        st.divider()
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state['user_id'] = None
            st.session_state['role'] = None
            st.rerun()

    # --- KHU VỰC HIỂN THỊ CHÍNH ---
    st.title("Trang Quản trị Hệ thống")
    
    if admin_menu == "📊 Thống kê Tổng quan":
        st.markdown("Chào mừng **Admin**! Dưới đây là tình trạng hoạt động của hệ thống.")
        
        # Tạo 3 thẻ thống kê giả lập
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Tổng số Ứng viên", value="1,245", delta="+12 hôm nay")
        col2.metric(label="Công việc (JD) hiện có", value="50", delta="0")
        col3.metric(label="Lượt gọi API AI", value="342", delta="-15")
        
        st.info("💡 Lưu ý: Các chức năng chi tiết sẽ được xây dựng sau.")
        
    elif admin_menu == "👥 Quản lý Người dùng": 
        user_management_page()
        
    else:
        # Các tab khác báo đang xây dựng
        st.warning(f"🚧 Chức năng **{admin_menu}** đang trong quá trình phát triển!")