# File: services/auth/email_auth.py
"""
Concrete Strategy: Xác thực bằng Email + Mật khẩu.
Đây là phương thức xác thực truyền thống, logic được bưng từ user_service.py cũ.
"""
from services.auth.base import IAuthStrategy, AuthResult
from repositories.database import db_session
from repositories.user_repo import get_user_by_email, create_user
from services.auth_service import verify_password


class EmailAuth(IAuthStrategy):
    """Chiến lược xác thực bằng Email và Mật khẩu."""

    def login(self, email: str = "", password: str = "", **kwargs) -> AuthResult:
        """Đăng nhập bằng Email.
        
        Args:
            email: Địa chỉ email người dùng.
            password: Mật khẩu dạng plain text.
        """
        if not email or not password:
            return AuthResult(error="Vui lòng nhập đầy đủ Email và Mật khẩu!")

        with db_session() as db:
            user = get_user_by_email(db, email)
            if user and user.password_hash and verify_password(password, user.password_hash):
                return AuthResult(user_id=user.id, role=user.role)
        return AuthResult(error="Sai Email hoặc Mật khẩu!")

    def register(self, full_name: str = "", email: str = "", password: str = "",
                 password_confirm: str = "", role: str = "user", **kwargs) -> AuthResult:
        """Đăng ký tài khoản bằng Email.
        
        Args:
            full_name: Họ tên (hoặc tên công ty nếu là nhà tuyển dụng).
            email: Địa chỉ email.
            password: Mật khẩu.
            password_confirm: Xác nhận mật khẩu.
            role: Vai trò (user hoặc job_poster).
        """
        if not full_name or not email or not password:
            return AuthResult(error="Vui lòng điền đầy đủ thông tin!")
        if password != password_confirm:
            return AuthResult(error="Mật khẩu xác nhận không khớp!")

        with db_session() as db:
            new_user = create_user(db, email, password, full_name, role, auth_provider='email')
            if new_user:
                return AuthResult(user_id=new_user.id, role=new_user.role)
        return AuthResult(error="⚠️ Email này đã được sử dụng. Vui lòng chọn email khác!")
