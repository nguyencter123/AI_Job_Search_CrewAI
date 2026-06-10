# File: app.py
import streamlit as st

from services.user_service import get_user_role, check_profile_complete
from views.admin.admin_dashboard import render_admin_dashboard
from views.auth_ui import render_auth_page
from views.dashboard import render_dashboard
from views.profile_setup_ui import render_profile_setup

st.set_page_config(page_title="AI Job Search Assistant", page_icon="💼", layout="wide")


def main():
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "role" not in st.session_state:
        st.session_state["role"] = None

    if st.session_state["user_id"] is None:
        render_auth_page()
        return

    uid = st.session_state["user_id"]

    if st.session_state.get("role") is None:
        st.session_state["role"] = get_user_role(uid)

    if st.session_state.get("role") == "admin":
        render_admin_dashboard()
        return

    profile_done = check_profile_complete(uid)

    if st.session_state.get("role") == "job_poster":
        from views.employer.profile_setup_ui import render_employer_profile_setup
        from views.employer.employer_dashboard import render_employer_dashboard
        
        if not profile_done:
            render_employer_profile_setup()
        else:
            render_employer_dashboard()
        return

    # Routing cho User bình thường
    if not profile_done:
        render_profile_setup()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
