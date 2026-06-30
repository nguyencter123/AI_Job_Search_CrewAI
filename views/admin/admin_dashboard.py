# File: views/admin/admin_dashboard.py
"""
Admin Dashboard — Tích hợp:
- Thống kê tổng quan (code cũ)
- Quản lý người dùng (code từ nhánh phan-cao)
"""
import streamlit as st
from views.utils import load_css
from views.admin.admin_management import user_management_page
from services.admin_service import AdminFacade


def render_admin_dashboard():
    load_css("assets/style.css")

    # --- THANH ĐIỀU HƯỚNG CỦA ADMIN ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #dc2626;'>🛡️ Admin Panel</h2>", unsafe_allow_html=True)
        st.caption("<div style='text-align: center;'>Quyền quản trị tối cao</div>", unsafe_allow_html=True)
        st.divider()

        admin_menu = st.radio(
            "📍 Quản lý hệ thống",
            ["📊 Thống kê Tổng quan", "👥 Quản lý Người dùng", "⚙️ Cài đặt AI Models"],
            label_visibility="collapsed"
        )

        st.spacer = st.container()
        st.divider()
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- KHU VỰC HIỂN THỊ CHÍNH ---
    if admin_menu == "📊 Thống kê Tổng quan":
        st.title("📊 Thống kê Tổng quan")
        st.markdown("Chào mừng **Admin**! Dưới đây là tình trạng hoạt động của hệ thống.")

        # Lấy dữ liệu thống kê thực từ AdminFacade
        stats = AdminFacade.get_statistics()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="Tổng User", value=stats.get("total_users", 0))
        col2.metric(label="Hoạt động", value=stats.get("active_users", 0))
        col3.metric(label="Bị khóa", value=stats.get("blocked_users", 0))
        col4.metric(label="Admin", value=stats.get("admin_count", 0))

        st.divider()
        st.markdown("### 📧 Quản trị Thông báo (Test)")
        st.write("Chức năng này cho phép Admin kích hoạt thủ công luồng gửi Thông báo việc làm mới thay vì phải chờ đến 8h sáng.")
        
        col_test_1, col_test_2, col_test_3 = st.columns(3)
        
        with col_test_1:
            test_all = st.button("🚀 Chạy gửi TẤT CẢ (Email + Tele)", type="primary", use_container_width=True)
        with col_test_2:
            test_email = st.button("📧 Chỉ test Gửi Email", use_container_width=True)
        with col_test_3:
            test_tele = st.button("✈️ Chỉ test Gửi Telegram", use_container_width=True)
            
        channel = None
        if test_all:
            channel = "all"
        elif test_email:
            channel = "email"
        elif test_tele:
            channel = "telegram"
            
        if channel:
            from services.notification_service import run_daily_notification
            with st.spinner(f"Đang chạy Observer Pattern ({channel})... Lấy danh sách job, chấm điểm AI và gửi..."):
                result = run_daily_notification(channel=channel)
                
            if result.get("total_users") == 0 or result.get("total_jobs") == 0:
                st.info(result.get("message"))
            else:
                st.success(result.get("message"))
                
                # Hiển thị chi tiết kết quả từ các Observer
                st.write("**Chi tiết kết quả:**")
                st.json(result)

    elif admin_menu == "👥 Quản lý Người dùng":
        user_management_page()

    else:
        # Các tab khác báo đang xây dựng
        st.title(admin_menu)
        st.warning(f"🚧 Chức năng **{admin_menu}** đang trong quá trình phát triển!")