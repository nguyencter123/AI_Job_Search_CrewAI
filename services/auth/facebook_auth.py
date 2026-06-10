# File: services/auth/facebook_auth.py
"""
Concrete Strategy: Xác thực bằng Facebook OAuth 2.0.
Luồng hoạt động:
1. UI tạo link chuyển hướng sang Facebook.
2. User đồng ý → Facebook redirect về localhost kèm ?code=XYZ.
3. Class này nhận code → Đổi lấy access_token → Lấy thông tin user.
4. Tìm hoặc tạo User mới trong DB dựa trên facebook_id.
"""
import os
import requests
from dotenv import load_dotenv

from services.auth.base import IAuthStrategy, AuthResult
from repositories.database import db_session
from repositories.user_repo import get_user_by_facebook_id, create_user_from_facebook

load_dotenv()


class FacebookAuth(IAuthStrategy):
    """Chiến lược xác thực bằng Facebook OAuth 2.0."""

    FB_APP_ID = os.getenv("FB_APP_ID", "")
    FB_APP_SECRET = os.getenv("FB_APP_SECRET", "")
    # Hardcode để tránh lỗi ký tự ẩn từ .env
    FB_REDIRECT_URI = "http://localhost:8501"

    @staticmethod
    def get_login_url() -> str:
        """Tạo URL chuyển hướng sang trang xác thực Facebook."""
        return (
            f"https://www.facebook.com/v19.0/dialog/oauth"
            f"?client_id={FacebookAuth.FB_APP_ID}"
            f"&redirect_uri={FacebookAuth.FB_REDIRECT_URI}"
            f"&scope=public_profile"
        )

    def login(self, code: str = "", **kwargs) -> AuthResult:
        """Đăng nhập bằng Facebook OAuth.
        
        Args:
            code: Mã xác thực (authorization code) Facebook trả về qua URL.
        """
        if not code:
            return AuthResult(error="Không nhận được mã xác thực từ Facebook!")

        # Bước 1: Đổi code lấy access_token
        # QUAN TRỌNG: Xây dựng URL thủ công (KHÔNG dùng params=) để redirect_uri
        # khớp 100% với URL authorization ở trên.
        token_url = (
            f"https://graph.facebook.com/v19.0/oauth/access_token"
            f"?client_id={self.FB_APP_ID}"
            f"&client_secret={self.FB_APP_SECRET}"
            f"&redirect_uri={self.FB_REDIRECT_URI}"
            f"&code={code}"
        )
        try:
            resp = requests.get(token_url, timeout=10)

            if resp.status_code != 200:
                fb_error = resp.json().get("error", {}).get("message", resp.text)
                return AuthResult(error=f"Xác thực Facebook thất bại: {fb_error}")

            access_token = resp.json().get("access_token")
            if not access_token:
                return AuthResult(error="Không lấy được access token từ Facebook!")

        except requests.RequestException as e:
            return AuthResult(error=f"Lỗi kết nối Facebook: {e}")

        # Bước 2: Dùng access_token để lấy thông tin cá nhân
        try:
            me_url = "https://graph.facebook.com/me"
            me_resp = requests.get(me_url, params={
                "access_token": access_token,
                "fields": "id,name",
            }, timeout=10)
            fb_data = me_resp.json()
        except requests.RequestException as e:
            return AuthResult(error=f"Lỗi lấy thông tin Facebook: {e}")

        fb_id = fb_data.get("id")
        fb_name = fb_data.get("name", "Facebook User")

        if not fb_id:
            return AuthResult(error="Không lấy được ID Facebook!")

        # Bước 3: Tìm hoặc tạo User trong DB
        with db_session() as db:
            user = get_user_by_facebook_id(db, fb_id)
            if not user:
                # Lần đầu đăng nhập bằng Facebook → Tự động tạo tài khoản mới
                user = create_user_from_facebook(db, fb_id, fb_name)
            if user:
                return AuthResult(user_id=user.id, role=user.role)

        return AuthResult(error="Không thể tạo tài khoản từ Facebook!")

    def register(self, **kwargs) -> AuthResult:
        """Facebook không cần trang đăng ký riêng.
        Khi user đăng nhập lần đầu, hệ thống sẽ TỰ ĐỘNG tạo tài khoản.
        """
        return self.login(**kwargs)
