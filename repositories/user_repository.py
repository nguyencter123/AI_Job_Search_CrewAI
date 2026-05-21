from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from repositories.database import SessionLocal
from repositories.models import User


# =========================
# LẤY TẤT CẢ USER
# =========================
def fetch_all_users():
    db: Session = SessionLocal()

    try:
        users = db.query(User).order_by(User.created_at.desc()).all()

        return [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at
            }
            for u in users
        ]

    except SQLAlchemyError:
        return []

    finally:
        db.close()


# =========================
# TÌM USER
# =========================
def search_users(keyword):
    db: Session = SessionLocal()

    try:
        users = db.query(User).filter(
            User.email.ilike(f"%{keyword}%")
        ).all()

        return [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at
            }
            for u in users
        ]

    finally:
        db.close()


# =========================
# FILTER USER
# =========================
def filter_users(role=None, is_active=None):
    db: Session = SessionLocal()

    query = db.query(User)

    if role and role != "all":
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.all()

    db.close()

    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at
        }
        for u in users
    ]


# =========================
# LẤY 1 USER
# =========================
def get_user_by_id(user_id):
    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()

    db.close()

    return user


# =========================
# KHÓA / MỞ KHÓA
# =========================
def update_user_status(user_id, status, current_admin_id=None):
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False, "User không tồn tại"

        if user.id == current_admin_id:
            return False, "Admin không thể tự khóa mình"

        user.is_active = status

        db.commit()

        return True, "Cập nhật thành công"

    except:
        db.rollback()
        return False, "Lỗi database"

    finally:
        db.close()


# =========================
# XÓA USER
# =========================
def remove_user(user_id, current_admin_id=None):
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False, "User không tồn tại"

        if user.id == current_admin_id:
            return False, "Admin không thể tự xóa"

        if user.role == "admin":
            return False, "Không được xóa tài khoản admin"

        db.delete(user)
        db.commit()

        return True, "Đã xóa user"

    except:
        db.rollback()
        return False, "Lỗi database"

    finally:
        db.close()


# =========================
# THỐNG KÊ
# =========================
def get_user_statistics():
    db = SessionLocal()

    total_users = db.query(User).count()

    active_users = db.query(User).filter(
        User.is_active == True
    ).count()

    blocked_users = db.query(User).filter(
        User.is_active == False
    ).count()

    admin_count = db.query(User).filter(
        User.role == "admin"
    ).count()

    db.close()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "blocked_users": blocked_users,
        "admin_count": admin_count
    }