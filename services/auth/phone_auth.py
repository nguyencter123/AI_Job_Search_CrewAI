# File: services/auth/phone_auth.py
"""
Concrete Strategy: Xác thực bằng Số điện thoại + Mật khẩu.
Logic tương tự EmailAuth, chỉ khác identifier là phone_number thay vì email.
"""
from services.auth.base import IAuthStrategy, AuthResult
from repositories.database import db_session
from repositories.user_repo import get_user_by_phone, create_user_with_phone
from services.auth_service import verify_password


class PhoneAuth(IAuthStrategy):
    """Chiến lược xác thực bằng Số điện thoại và Mật khẩu."""

    def login(self, phone: str = "", password: str = "", **kwargs) -> AuthResult:
        """Đăng nhập bằng Số điện thoại.
        
        Args:
            phone: Số điện thoại.
            password: Mật khẩu dạng plain text.
        """
        if not phone or not password:
            return AuthResult(error="Vui lòng nhập đầy đủ Số điện thoại và Mật khẩu!")

        with db_session() as db:
            user = get_user_by_phone(db, phone)
            if user and user.password_hash and verify_password(password, user.password_hash):
                return AuthResult(user_id=user.id, role=user.role)
        return AuthResult(error="Sai Số điện thoại hoặc Mật khẩu!")

    def register(self, full_name: str = "", phone: str = "", password: str = "",
                 password_confirm: str = "", role: str = "user", **kwargs) -> AuthResult:
        """Đăng ký tài khoản bằng Số điện thoại.
        
        Args:
            full_name: Họ tên (hoặc tên công ty).
            phone: Số điện thoại.
            password: Mật khẩu.
            password_confirm: Xác nhận mật khẩu.
            role: Vai trò.
        """
        if not full_name or not phone or not password:
            return AuthResult(error="Vui lòng điền đầy đủ thông tin!")
        if password != password_confirm:
            return AuthResult(error="Mật khẩu xác nhận không khớp!")

        with db_session() as db:
            new_user = create_user_with_phone(db, phone, password, full_name, role)
            if new_user:
                return AuthResult(user_id=new_user.id, role=new_user.role)
        return AuthResult(error="⚠️ Số điện thoại này đã được sử dụng!")
