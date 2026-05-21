import streamlit as st

from services.admin_service import AdminFacade


def user_management_page():
    st.header("👥 Quản lý Người dùng")

    # =========================
    # STATS
    # =========================
    stats = AdminFacade.get_statistics()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Tổng User", stats["total_users"])
    c2.metric("Hoạt động", stats["active_users"])
    c3.metric("Bị khóa", stats["blocked_users"])
    c4.metric("Admin", stats["admin_count"])

    st.divider()

    # =========================
    # SEARCH + FILTER
    # =========================
    col1, col2, col3 = st.columns(3)

    with col1:
        keyword = st.text_input("🔍 Tìm email")

    with col2:
        role_filter = st.selectbox(
            "Role",
            ["all", "user", "admin"]
        )

    with col3:
        status_filter = st.selectbox(
            "Status",
            ["all", "active", "blocked"]
        )

    # Query logic
    if keyword:
        users = AdminFacade.search_users(keyword)

    else:
        if status_filter == "all":
            active = None
        elif status_filter == "active":
            active = True
        else:
            active = False

        users = AdminFacade.filter_users(
            role_filter,
            active
        )

    st.divider()

    # =========================
    # USER LIST
    # =========================
    for user in users:
        col1, col2, col3, col4 = st.columns([4, 2, 2, 2])

        with col1:
            st.write(f"**{user['email']}** ({user['role']})")

        with col2:
            st.write(
                "🟢 Active"
                if user["is_active"]
                else "🔴 Blocked"
            )

        with col3:
            button_label = (
                "Khóa"
                if user["is_active"]
                else "Mở"
            )

            if st.button(
                button_label,
                key=f"lock_{user['id']}"
            ):
                success, msg = AdminFacade.update_user_status(
                    user["id"],
                    not user["is_active"],
                    st.session_state["user_id"]
                )

                if success:
                    st.success(msg)
                else:
                    st.error(msg)

                st.rerun()

        with col4:
            is_self = (
                user["id"] ==
                st.session_state["user_id"]
            )

            if st.button(
                "Xóa",
                key=f"delete_{user['id']}",
                disabled=is_self
            ):
                success, msg = AdminFacade.remove_user(
                    user["id"],
                    st.session_state["user_id"]
                )

                if success:
                    st.success(msg)
                else:
                    st.error(msg)

                st.rerun()