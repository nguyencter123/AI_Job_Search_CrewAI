import streamlit as st

from repositories.user_repository import (
    fetch_all_users,
    search_users,
    filter_users,
    update_user_status,
    remove_user,
    get_user_statistics
)


def user_management_page():
    st.header("👥 Quản lý Người dùng")

    # =================
    # STATISTICS
    # =================
    stats = get_user_statistics()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Tổng User", stats["total_users"])
    c2.metric("Đang hoạt động", stats["active_users"])
    c3.metric("Bị khóa", stats["blocked_users"])
    c4.metric("Admin", stats["admin_count"])

    st.divider()

    # =================
    # SEARCH + FILTER
    # =================
    col1, col2, col3 = st.columns(3)

    with col1:
        search = st.text_input("🔍 Tìm email")

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

    # Logic
    if search:
        users = search_users(search)

    else:
        if status_filter == "all":
            active = None
        elif status_filter == "active":
            active = True
        else:
            active = False

        users = filter_users(role_filter, active)

    st.divider()

    # =================
    # USER LIST
    # =================
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
            label = (
                "Khóa"
                if user["is_active"]
                else "Mở"
            )

            if st.button(label, key=f"lock_{user['id']}"):
                success, msg = update_user_status(
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
                key=f"del_{user['id']}",
                disabled=is_self
            ):
                success, msg = remove_user(
                    user["id"],
                    st.session_state["user_id"]
                )

                if success:
                    st.success(msg)
                else:
                    st.error(msg)

                st.rerun()