# File: repositories/user_repo.py
from sqlalchemy.orm import Session
from .models import User, UserProfile, EmployerProfile
from services.auth_service import hash_password

def get_user_by_email(db: Session, email: str):
    """Tìm người dùng theo email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db: Session, phone: str):
    """Tìm người dùng theo số điện thoại."""
    return db.query(User).filter(User.phone_number == phone).first()


def get_user_by_facebook_id(db: Session, facebook_id: str):
    """Tìm người dùng theo Facebook ID."""
    return db.query(User).filter(User.facebook_id == facebook_id).first()


def get_user_by_id(db: Session, user_id: int):
    """Tìm người dùng theo khóa chính."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_and_profile(db: Session, user_id: int):
    """Lấy User và UserProfile trong cùng một phiên DB."""
    user = get_user_by_id(db, user_id)
    if not user:
        return None, None
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    return user, profile


def create_user(db: Session, email: str, password: str, full_name: str, 
                role: str = 'user', auth_provider: str = 'email'):
    """Tạo tài khoản mới bằng Email và khởi tạo Profile trống tương ứng."""
    existing_user = get_user_by_email(db, email)
    if existing_user:
        return None

    hashed_pw = hash_password(password)
    new_user = User(email=email, password_hash=hashed_pw, role=role, auth_provider=auth_provider)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if role == 'job_poster':
        new_profile = EmployerProfile(user_id=new_user.id, company_name=full_name)
    else:
        new_profile = UserProfile(user_id=new_user.id, full_name=full_name)
        
    db.add(new_profile)
    db.commit()
    return new_user


def create_user_with_phone(db: Session, phone: str, password: str, full_name: str,
                           role: str = 'user'):
    """Tạo tài khoản mới bằng Số điện thoại."""
    existing_user = get_user_by_phone(db, phone)
    if existing_user:
        return None

    hashed_pw = hash_password(password)
    new_user = User(phone_number=phone, password_hash=hashed_pw, role=role, auth_provider='phone')
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if role == 'job_poster':
        new_profile = EmployerProfile(user_id=new_user.id, company_name=full_name)
    else:
        new_profile = UserProfile(user_id=new_user.id, full_name=full_name)

    db.add(new_profile)
    db.commit()
    return new_user


def create_user_from_facebook(db: Session, facebook_id: str, full_name: str,
                              role: str = 'user'):
    """Tạo tài khoản mới từ Facebook OAuth (không cần mật khẩu)."""
    existing_user = get_user_by_facebook_id(db, facebook_id)
    if existing_user:
        return existing_user  # Trả về user hiện có thay vì tạo mới

    new_user = User(facebook_id=facebook_id, role=role, auth_provider='facebook')
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

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


def update_user_contact(db: Session, user_id: int, email: str, phone: str):
    """Cập nhật email và số điện thoại cho User.
    
    Cho phép mọi tài khoản (dù tạo bằng Email, Phone hay Facebook)
    đều có thể bổ sung đầy đủ thông tin liên hệ.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None, "Không tìm thấy tài khoản."
    
    # Kiểm tra email trùng (nếu có thay đổi)
    if email and email != user.email:
        existing = db.query(User).filter(User.email == email, User.id != user_id).first()
        if existing:
            return None, "Email này đã được sử dụng bởi tài khoản khác."
    
    # Kiểm tra SĐT trùng (nếu có thay đổi)
    if phone and phone != user.phone_number:
        existing = db.query(User).filter(User.phone_number == phone, User.id != user_id).first()
        if existing:
            return None, "Số điện thoại này đã được sử dụng bởi tài khoản khác."
    
    user.email = email if email else user.email
    user.phone_number = phone if phone else user.phone_number
    db.commit()
    return user, None


def update_user_avatar(db: Session, user_id: int, avatar_bytes: bytes, mimetype: str):
    """Cập nhật ảnh đại diện cho Profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        profile.avatar_data = avatar_bytes
        profile.avatar_mimetype = mimetype
        db.commit()
        return profile
    return None


def get_user_avatar(db: Session, user_id: int) -> tuple[bytes | None, str | None]:
    """Lấy ảnh đại diện (bytes) và mimetype."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile and profile.avatar_data:
        return profile.avatar_data, profile.avatar_mimetype
    return None, None


def is_profile_complete(db: Session, user_id: int) -> bool:
    """Kiểm tra xem người dùng đã nhập đầy đủ thông tin hồ sơ chưa"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
        
    if user.role == 'job_poster':
        profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == user_id).first()
        # Hồ sơ nhà tuyển dụng hoàn thiện khi có company_description và address
        return bool(profile and profile.company_description and profile.address)
    else:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        return bool(profile and profile.skills and profile.experience_summary and profile.avatar_data)

def update_employer_profile(db: Session, user_id: int, company_name: str, description: str, website: str, address: str):
    """Cập nhật thông tin chi tiết cho EmployerProfile"""
    profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == user_id).first()
    if profile:
        profile.company_name = company_name
        profile.company_description = description
        profile.website = website
        profile.address = address
        db.commit()
        return profile
    return None


def get_users_for_notification(db: Session):
    """Lấy danh sách user đủ điều kiện nhận email hoặc telegram thông báo.
    
    Điều kiện:
    - Nhận email (receive_daily_email = True) HOẶC có telegram (telegram_chat_id != None)
    - Đã điền kỹ năng (skills không rỗng)
    
    Returns: list of (User, UserProfile) tuples
    """
    from sqlalchemy import or_, and_
    results = (
        db.query(User, UserProfile)
        .join(UserProfile, User.id == UserProfile.user_id)
        .filter(
            or_(
                UserProfile.receive_daily_email == True,
                and_(
                    UserProfile.receive_daily_telegram == True,
                    UserProfile.telegram_chat_id.isnot(None)
                )
            ),
            UserProfile.skills.isnot(None),
            UserProfile.skills != "",
            User.is_active == True,
        )
        .all()
    )
    return results


def update_receive_email(db: Session, user_id: int, receive: bool):
    """Bật/tắt nhận email thông báo việc làm cho user."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        profile.receive_daily_email = receive
        db.commit()
        return True
    return False

def update_receive_telegram(db: Session, user_id: int, receive: bool):
    """Bật/tắt nhận Telegram thông báo cho user."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        profile.receive_daily_telegram = receive
        db.commit()
        return True
    return False

def update_telegram_chat_id(db: Session, user_id: int, chat_id: str):
    """Cập nhật Telegram Chat ID cho user."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        profile.telegram_chat_id = chat_id if chat_id else None
        db.commit()
        return True
    return False