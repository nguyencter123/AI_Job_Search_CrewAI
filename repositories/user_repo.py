# File: repositories/user_repo.py
from sqlalchemy.orm import Session
from .models import User, UserProfile
from services.auth_service import hash_password

def get_user_by_email(db: Session, email: str):
    """Tìm người dùng theo email."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str, full_name: str):
    """Tạo tài khoản mới và khởi tạo luôn một Profile trống."""
    # 1. Kiểm tra xem email đã tồn tại chưa
    existing_user = get_user_by_email(db, email)
    if existing_user:
        return None  # Trả về None nếu email đã bị trùng

    # 2. Tạo User với mật khẩu đã mã hóa
    hashed_pw = hash_password(password)
    new_user = User(email=email, password_hash=hashed_pw, role='user')
    db.add(new_user)
    db.commit()      # Lưu User để lấy được id
    db.refresh(new_user)

    # 3. Tạo ngay một Profile trống đi kèm với User này
    new_profile = UserProfile(user_id=new_user.id, full_name=full_name)
    db.add(new_profile)
    db.commit()

    return new_user
# repositories/user_repo.py

def update_user_profile(db: Session, user_id: int, skills: str, experience: str):
    """Cập nhật thông tin chi tiết cho Profile"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        profile.skills = skills
        profile.experience_summary = experience
        db.commit()
        return profile
    return None

def is_profile_complete(db: Session, user_id: int) -> bool:
    """Kiểm tra xem người dùng đã nhập kỹ năng và kinh nghiệm chưa"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    return bool(profile and profile.skills and profile.experience_summary)