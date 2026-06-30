# File: services/auth/base.py
"""
Interface (Khuôn mẫu) cho Factory Design Pattern.
Mọi phương thức xác thực (Email, Phone, ...) đều PHẢI kế thừa IAuthStrategy
và triển khai đầy đủ các phương thức login() và register().
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AuthResult:
    """Kết quả trả về thống nhất cho MỌI phương thức đăng nhập/đăng ký.
    
    Attributes:
        user_id: ID của user nếu thành công, None nếu thất bại.
        role: Vai trò của user (user, admin, job_poster).
        error: Thông báo lỗi nếu có, None nếu thành công.
    """
    user_id: int | None = None
    role: str | None = None
    error: str | None = None


class IAuthStrategy(ABC):
    """Abstract Base Class: Hợp đồng bắt buộc cho mọi chiến lược xác thực.
    
    
    """

    @abstractmethod
    def login(self, **kwargs) -> AuthResult:
        """Xác thực đăng nhập.
        
        Args:
            **kwargs: Các tham số đầu vào tùy theo phương thức
                      (email/password, phone/password, hoặc OAuth code).
        Returns:
            AuthResult chứa user_id + role nếu thành công, hoặc error nếu thất bại.
        """
        pass

    @abstractmethod
    def register(self, **kwargs) -> AuthResult:
        """Đăng ký tài khoản mới.
        
        Args:
            **kwargs: Các tham số đầu vào tùy theo phương thức.
        Returns:
            AuthResult chứa user_id + role nếu thành công, hoặc error nếu thất bại.
        """
        pass
