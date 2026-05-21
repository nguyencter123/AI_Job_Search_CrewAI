from repositories.database import SessionLocal
from repositories.admin_repository import AdminRepository


class AdminFacade:

    # ======================
    # FORMAT USER
    # ======================
    @staticmethod
    def _format_user(user):
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }

    # ======================
    # STATS
    # ======================
    @staticmethod
    def get_statistics():
        db = SessionLocal()

        try:
            return {
                "total_users": AdminRepository.count_users(db),
                "active_users": AdminRepository.count_active_users(db),
                "blocked_users": AdminRepository.count_blocked_users(db),
                "admin_count": AdminRepository.count_admins(db)
            }

        finally:
            db.close()

    # ======================
    # GET USERS
    # ======================
    @staticmethod
    def get_users(keyword="", role="all", active=None):
        db = SessionLocal()

        try:
            users = AdminRepository.get_users(
                db,
                keyword=keyword,
                role=role,
                active=active
            )

            return [
                AdminFacade._format_user(user)
                for user in users
            ]

        finally:
            db.close()

    # ======================
    # LOCK / UNLOCK USER
    # ======================
    @staticmethod
    def update_user_status(
        user_id,
        new_status,
        current_admin_id
    ):
        db = SessionLocal()

        try:
            user = AdminRepository.get_user_by_id(
                db,
                user_id
            )

            if not user:
                return False, "Người dùng không tồn tại"

            if user.id == current_admin_id:
                return False, "Không thể khóa chính mình"

            user.is_active = new_status
            AdminRepository.save(db)

            if new_status:
                return True, "Đã mở tài khoản"

            return True, "Đã khóa tài khoản"

        except Exception as e:
            db.rollback()
            return False, str(e)

        finally:
            db.close()

    # ======================
    # DELETE USER
    # ======================
    @staticmethod
    def remove_user(
        user_id,
        current_admin_id
    ):
        db = SessionLocal()

        try:
            user = AdminRepository.get_user_by_id(
                db,
                user_id
            )

            if not user:
                return False, "Người dùng không tồn tại"

            if user.id == current_admin_id:
                return False, "Không thể xóa chính mình"

            # delete children manually
            for match in user.matches:
                db.delete(match)

            for doc in user.documents:
                db.delete(doc)

            if user.profile:
                db.delete(user.profile)

            AdminRepository.delete(db, user)
            AdminRepository.save(db)

            return True, "Đã xóa user"

        except Exception as e:
            db.rollback()
            return False, str(e)

        finally:
            db.close()