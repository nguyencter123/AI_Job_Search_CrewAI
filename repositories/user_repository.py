from sqlalchemy.orm import Session
from repositories.models import User


# =========================
# GET USERS
# =========================
def get_all_users(db: Session):
    return db.query(User).order_by(User.created_at.desc()).all()


def search_users_by_email(db: Session, keyword):
    return db.query(User).filter(
        User.email.ilike(f"%{keyword}%")
    ).all()


def filter_users(db: Session, role=None, is_active=None):
    query = db.query(User)

    if role and role != "all":
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.all()


# =========================
# GET ONE USER
# =========================
def get_user_by_id(db: Session, user_id):
    return db.query(User).filter(User.id == user_id).first()


# =========================
# UPDATE STATUS
# =========================
def set_user_status(db: Session, user_id, status):
    user = get_user_by_id(db, user_id)

    if user:
        user.is_active = status

    return user


# =========================
# DELETE USER
# =========================
def delete_user(db: Session, user_id):
    user = get_user_by_id(db, user_id)

    if user:
        db.delete(user)

    return user


# =========================
# COUNT STATISTICS
# =========================
def count_total_users(db: Session):
    return db.query(User).count()


def count_active_users(db: Session):
    return db.query(User).filter(
        User.is_active == True
    ).count()


def count_blocked_users(db: Session):
    return db.query(User).filter(
        User.is_active == False
    ).count()


def count_admin_users(db: Session):
    return db.query(User).filter(
        User.role == "admin"
    ).count()