from repositories.database import SessionLocal
from repositories.models import User

from repositories.user_repository import (
    get_all_users,
    search_users_by_email,
    filter_users,
    get_user_by_id,
    set_user_status,
    delete_user,
    count_total_users,
    count_active_users,
    count_blocked_users,
    count_admin_users
)


class AdminFacade:

    # =========================
    # FORMAT USER
    # =========================
    @staticmethod
    def _format_user(user):
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at
        }

    # =========================
    # GET USERS
    # =========================
    @staticmethod
    def fetch_all_users():
        db = SessionLocal()

        try:
            users = get_all_users(db)

            return [
                AdminFacade._format_user(u)
                for u in users
            ]

        finally:
            db.close()

    @staticmethod
    def search_users(keyword):
        db = SessionLocal()

        try:
            users = search_users_by_email(db, keyword)

            return [
                AdminFacade._format_user(u)
                for u in users
            ]

        finally:
            db.close()

    @staticmethod
    def filter_users(role=None, is_active=None):
        db = SessionLocal()

        try:
            users = filter_users(db, role, is_active)

            return [
                AdminFacade._format_user(u)
                for u in users
            ]

        finally:
            db.close()

    # =========================
    # UPDATE STATUS
    # =========================
    @staticmethod
    def update_user_status(user_id, status, current_admin_id):
        db = SessionLocal()

        try:
            user = get_user_by_id(db, user_id)

            if not user:
                return False, "User không tồn tại"

            if user.id == current_admin_id:
                return False, "Admin không thể tự khóa"

            set_user_status(db, user_id, status)

            db.commit()

            return True, "Cập nhật thành công"

        except:
            db.rollback()
            return False, "Lỗi database"

        finally:
            db.close()

    # =========================
    # DELETE USER
    # =========================
    @staticmethod
    def remove_user(user_id, current_admin_id):
        db = SessionLocal()

        try:
            user = get_user_by_id(db, user_id)

            if not user:
                return False, "User không tồn tại"

            if user.id == current_admin_id:
                return False, "Không thể tự xóa"

            if user.role == "admin":
                return False, "Không được xóa admin"

            delete_user(db, user_id)

            db.commit()

            return True, "Đã xóa user"

        except:
            db.rollback()
            return False, "Lỗi database"

        finally:
            db.close()

    # =========================
    # STATISTICS
    # =========================
    @staticmethod
    def get_statistics():
        db = SessionLocal()

        try:
            return {
                "total_users": count_total_users(db),
                "active_users": count_active_users(db),
                "blocked_users": count_blocked_users(db),
                "admin_count": count_admin_users(db)
            }

        finally:
            db.close()