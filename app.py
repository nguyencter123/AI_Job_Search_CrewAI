# File: app.py
import streamlit as st
from views.auth_ui import render_auth_page
from views.dashboard import render_dashboard
from views.profile_setup_ui import render_profile_setup
from repositories.database import SessionLocal
from repositories.models import User
from repositories.user_repo import is_profile_complete
from views.admin.admin_dashboard import render_admin_dashboard

st.set_page_config(page_title="AI Job Search Assistant", page_icon="💼", layout="wide")


def _get_role(user_id: int) -> str | None:
    """Lấy role của user từ DB (đề phòng session_state chưa có role)."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user.role if user else None
    finally:
        db.close()


def main():
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'role' not in st.session_state:
        st.session_state['role'] = None

    # 1. NẾU CHƯA ĐĂNG NHẬP -> Hiện Form Đăng nhập
    if st.session_state['user_id'] is None:
        render_auth_page()
    else:
        # 2. KIỂM TRA QUYỀN (ROLE)
        if st.session_state.get('role') == 'admin':
            # NẾU LÀ ADMIN -> Vào thẳng trang quản trị
            render_admin_dashboard()
        else:
            # NẾU LÀ USER BÌNH THƯỜNG -> Tiếp tục luồng cũ
            db = SessionLocal()
            try:
                profile_done = is_profile_complete(db, st.session_state['user_id'])
            finally:
                db.close()
                
            if not profile_done:
                render_profile_setup()
            else:
                render_dashboard()


if __name__ == "__main__":
    main()