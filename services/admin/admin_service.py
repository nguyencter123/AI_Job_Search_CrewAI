# File: services/admin_service.py
"""
Facade Pattern: Đóng gói mọi thao tác quản trị hệ thống.
View Admin chỉ gọi các hàm ở đây, không gọi trực tiếp repositories.
"""
from __future__ import annotations

from repositories.database import db_session
from repositories.models import User, UserProfile, UserJobMatch, ApplicationDocument
from repositories.job_provider import get_all_jobs


def get_dashboard_stats() -> dict:
    """
    Lấy thống kê tổng quan cho trang Admin Dashboard.

    Returns:
        dict chứa total_users, total_jobs, total_profiles_complete,
        total_matches, total_documents
    """
    with db_session() as db:
        total_users = db.query(User).count()
        total_profiles = db.query(UserProfile).filter(
            UserProfile.skills.isnot(None),
            UserProfile.skills != ""
        ).count()
        total_matches = db.query(UserJobMatch).count()
        total_documents = db.query(ApplicationDocument).count()

    total_jobs = len(get_all_jobs())

    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "total_profiles_complete": total_profiles,
        "total_matches": total_matches,
        "total_documents": total_documents,
    }


def list_all_users() -> list[dict]:
    """
    Lấy danh sách tất cả người dùng cho trang quản lý.

    Returns:
        list of dict chứa id, email, role, is_active, created_at
    """
    with db_session() as db:
        users = db.query(User).all()
        return [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at,
            }
            for u in users
        ]


def toggle_user_active(user_id: int) -> bool:
    """
    Bật/tắt trạng thái hoạt động của user.

    Returns:
        True nếu thành công, False nếu không tìm thấy user
    """
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = not user.is_active
            db.commit()
            return True
    return False
