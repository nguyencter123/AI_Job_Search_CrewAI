# File: services/user_service.py
"""
Facade Pattern: Đóng gói mọi thao tác liên quan đến User.
View chỉ gọi các hàm ở đây, không gọi trực tiếp repositories.
"""
from __future__ import annotations

from repositories.database import db_session
from repositories.user_repo import (
    get_user_by_email,
    get_user_by_id,
    get_user_and_profile,
    create_user as _repo_create_user,
    update_user_profile as _repo_update_profile,
    update_user_avatar as _repo_update_avatar,
    get_user_avatar as _repo_get_avatar,
    is_profile_complete as _repo_is_profile_complete,
    update_employer_profile as _repo_update_employer_profile,
    EmployerProfile
)
from services.auth_service import verify_password
from services.image_service import validate_avatar, process_avatar
from services.auth.auth_factory import AuthFactory
from services.auth.base import AuthResult


def login(method: str = "email", **kwargs) -> tuple[int | None, str | None, str | None]:
    """
    Xác thực đăng nhập thông qua Factory Pattern.
    
    Args:
        method: Phương thức đăng nhập ("email", "phone", "facebook").
        **kwargs: Các tham số tương ứng (email/password, phone/password, code).
    Returns:
        Tuple (user_id, role, error).
    """
    auth = AuthFactory.create(method)
    result: AuthResult = auth.login(**kwargs)
    return result.user_id, result.role, result.error


def register(method: str = "email", **kwargs) -> tuple[int | None, str | None, str | None]:
    """
    Đăng ký tài khoản mới thông qua Factory Pattern.
    
    Args:
        method: Phương thức đăng ký ("email", "phone", "facebook").
        **kwargs: Các tham số tương ứng.
    Returns:
        Tuple (user_id, role, error).
    """
    auth = AuthFactory.create(method)
    result: AuthResult = auth.register(**kwargs)
    return result.user_id, result.role, result.error


def get_user_info(user_id: int) -> dict | None:
    """
    Lấy toàn bộ thông tin hiển thị của user.

    """
    with db_session() as db:
        user, profile = get_user_and_profile(db, user_id)
        if not user:
            return None
        return {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "display_name": (
                profile.full_name if profile and profile.full_name else user.email
            ),
            "skills": (profile.skills if profile else "") or "",
            "experience_summary": (
                profile.experience_summary if profile else ""
            ) or "",
            "has_avatar": bool(profile and profile.avatar_data),
        }


def update_profile(
    user_id: int, skills: str, experience: str
) -> tuple[bool, str | None]:
    """
    Cập nhật kỹ năng và kinh nghiệm cho user.

    """
    with db_session() as db:
        result = _repo_update_profile(db, user_id, skills, experience)
        if result:
            return True, None
    return False, "Không tìm thấy hồ sơ để cập nhật."


def check_profile_complete(user_id: int) -> bool:
    """Kiểm tra user đã nhập đầy đủ kỹ năng và kinh nghiệm chưa."""
    with db_session() as db:
        return _repo_is_profile_complete(db, user_id)


def get_user_role(user_id: int) -> str | None:
    """Lấy role của user (dùng để đồng bộ session sau reload trình duyệt)."""
    with db_session() as db:
        user = get_user_by_id(db, user_id)
        return user.role if user else None


def upload_avatar(
    user_id: int, file_data: bytes, mimetype: str
) -> tuple[bool, str | None]:
    """
    Upload ảnh đại diện: Validate → Xử lý (Crop/Resize/Nén) → Lưu DB.
    """
    # Bước 1: Kiểm tra tính hợp lệ
    error = validate_avatar(file_data, mimetype)
    if error:
        return False, error

    # Bước 2: Xử lý ảnh (Crop, Resize, Nén)
    processed_bytes, processed_mime = process_avatar(file_data)

    # Bước 3: Lưu vào DB
    with db_session() as db:
        result = _repo_update_avatar(db, user_id, processed_bytes, processed_mime)
        if result:
            return True, None
    return False, "Không tìm thấy hồ sơ để lưu ảnh."


def get_avatar(user_id: int) -> tuple[bytes | None, str | None]:
    """Đọc ảnh đại diện từ DB."""
    with db_session() as db:
        return _repo_get_avatar(db, user_id)

def get_employer_info(user_id: int) -> dict | None:
    """Lấy thông tin công ty của nhà tuyển dụng."""
    with db_session() as db:
        user = get_user_by_id(db, user_id)
        if not user or user.role != 'job_poster':
            return None
        profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == user_id).first()
        if not profile:
            return None
        return {
            "company_name": profile.company_name,
            "company_description": profile.company_description or "",
            "website": profile.website or "",
            "address": profile.address or ""
        }

def update_employer_info(user_id: int, company_name: str, description: str, website: str, address: str) -> tuple[bool, str | None]:
    """Cập nhật thông tin công ty."""
    with db_session() as db:
        result = _repo_update_employer_profile(db, user_id, company_name, description, website, address)
        if result:
            return True, None
    return False, "Không tìm thấy hồ sơ nhà tuyển dụng để cập nhật."
