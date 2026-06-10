# File: services/auth/auth_factory.py
"""
Factory Pattern: Phân phối đúng chiến lược xác thực dựa theo method_type.

Sử dụng:
    auth = AuthFactory.create("email")
    result = auth.login(email="a@b.com", password="123")
    
    auth = AuthFactory.create("facebook")
    result = auth.login(code="abc123")
"""
from services.auth.base import IAuthStrategy
from services.auth.email_auth import EmailAuth
from services.auth.phone_auth import PhoneAuth
from services.auth.facebook_auth import FacebookAuth


class AuthFactory:
    """Nhà máy sản xuất ra đúng chiến lược xác thực theo yêu cầu.
    
    Để mở rộng (ví dụ: thêm Google Login), chỉ cần:
    1. Tạo file google_auth.py chứa class GoogleAuth(IAuthStrategy)
    2. Thêm "google": GoogleAuth vào _strategies
    3. Xong! Không cần sửa bất kỳ file nào khác.
    """

    _strategies: dict[str, type[IAuthStrategy]] = {
        "email": EmailAuth,
        "phone": PhoneAuth,
        "facebook": FacebookAuth,
    }

    @staticmethod
    def create(method: str) -> IAuthStrategy:
        """Tạo ra đúng đối tượng xác thực dựa theo phương thức được yêu cầu.
        
        Args:
            method: Tên phương thức ("email", "phone", "facebook").
            
        Returns:
            Một instance của IAuthStrategy tương ứng.
            
        Raises:
            ValueError: Nếu method không được hỗ trợ.
        """
        strategy_class = AuthFactory._strategies.get(method)
        if not strategy_class:
            raise ValueError(
                f"Phương thức xác thực '{method}' không được hỗ trợ! "
                f"Các phương thức hợp lệ: {list(AuthFactory._strategies.keys())}"
            )
        return strategy_class()
