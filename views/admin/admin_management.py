import streamlit as st
from services.admin_service import AdminFacade


def user_management_page():
    st.header("👥 Quản lý Người dùng")

    current_user_id = st.session_state.get("user_id")

    # =========================
    # STATS
    # =========================
    stats = AdminFacade.get_statistics()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Tổng User", stats.get("total_users", 0))
    c2.metric("Hoạt động", stats.get("active_users", 0))
    c3.metric("Bị khóa", stats.get("blocked_users", 0))
    c4.metric("Admin", stats.get("admin_count", 0))

    st.divider()

    # =========================
    # FILTER
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

    if status_filter == "all":
        active = None
    elif status_filter == "active":
        active = True
    else:
        active = False

    users = AdminFacade.get_users(
        keyword=keyword,
        role=role_filter,
        active=active
    )

    users = users or []

    st.divider()

    if not users:
        st.info("Không có người dùng")
        return

    # =========================
    # USER LIST
    # =========================
    for user in users:
        col1, col2, col3, col4 = st.columns([4, 2, 2, 2])

        with col1:
            st.write(
                f"**{user['email']}** ({user['role']})"
            )

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

            if st.button(
                label,
                key=f"lock_{user['id']}"
            ):
                success, msg = (
                    AdminFacade.update_user_status(
                        user["id"],
                        not user["is_active"],
                        current_user_id
                    )
                )

                if success:
                    st.success(msg)
                else:
                    st.error(msg)

                st.rerun()

        with col4:
            is_self = (
                user["id"] == current_user_id
            )

            if st.button(
                "Xóa",
                key=f"delete_{user['id']}",
                disabled=is_self
            ):
                success, msg = (
                    AdminFacade.remove_user(
                        user["id"],
                        current_user_id
                    )
                )

                if success:
                    st.success(msg)
                else:
                    st.error(msg)

                st.rerun()