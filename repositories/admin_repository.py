from sqlalchemy import func
from repositories.models import User


class AdminRepository:

    # ======================
    # COUNT
    # ======================
    @staticmethod
    def count_users(db):
        return db.query(User).count()

    @staticmethod
    def count_active_users(db):
        return db.query(User).filter(
            User.is_active == True
        ).count()

    @staticmethod
    def count_blocked_users(db):
        return db.query(User).filter(
            User.is_active == False
        ).count()

    @staticmethod
    def count_admins(db):
        return db.query(User).filter(
            User.role == "admin"
        ).count()

    # ======================
    # GET USERS
    # ======================
    @staticmethod
    def get_all_users(db):
        return db.query(User).all()

    @staticmethod
    def get_user_by_id(db, user_id):
        return db.query(User).filter(
            User.id == user_id
        ).first()

    @staticmethod
    def search_users(db, keyword):
        return db.query(User).filter(
            User.email.ilike(f"%{keyword}%")
        ).all()

    @staticmethod
    def filter_users(db, role="all", active=None):
        query = db.query(User)

        if role != "all":
            query = query.filter(User.role == role)

        if active is not None:
            query = query.filter(User.is_active == active)

        return query.all()

    @staticmethod
    def get_users(db, keyword="", role="all", active=None):
        query = db.query(User)

        if keyword:
            query = query.filter(
                User.email.ilike(f"%{keyword}%")
            )

        if role != "all":
            query = query.filter(
                User.role == role
            )

        if active is not None:
            query = query.filter(
                User.is_active == active
            )

        return query.all()

    # ======================
    # UPDATE
    # ======================
    @staticmethod
    def save(db):
        db.commit()

    @staticmethod
    def delete(db, obj):
        db.delete(obj)