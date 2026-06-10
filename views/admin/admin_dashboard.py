# File: views/admin/admin_dashboard.py
import streamlit as st
from services.admin.admin_service import get_dashboard_stats
from views.utils import load_css

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
            st.session_state.clear()
            st.rerun()

    # --- KHU VỰC HIỂN THỊ CHÍNH ---
    st.title("Trang Quản trị Hệ thống")
    
    if admin_menu == "📊 Thống kê Tổng quan":
        st.markdown("Chào mừng **Admin**! Dưới đây là tình trạng hoạt động của hệ thống.")
        
        # Lấy dữ liệu thống kê thực từ Facade
        stats = get_dashboard_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Tổng số Người dùng", value=f"{stats['total_users']:,}")
        col2.metric(label="Công việc (JD) hiện có", value=f"{stats['total_jobs']:,}")
        col3.metric(label="Hồ sơ đã hoàn thiện", value=f"{stats['total_profiles_complete']:,}")
        
    else:
        # Các tab khác báo đang xây dựng
        st.warning(f"🚧 Chức năng **{admin_menu}** đang trong quá trình phát triển!")