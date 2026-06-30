# File: services/ai_quota_service.py
"""
Quản lý Quota (Hạn mức) sử dụng AI cho tài khoản Freemium.

Quy tắc:
- Tài khoản Free: Tối đa 3 lần tạo CV + 3 lần AI Match / ngày.
- Tài khoản Pro: Không giới hạn (nhưng có ngày hết hạn).
- Bộ đếm tự động reset về 0 khi sang ngày mới.
- Khi Pro hết hạn, hệ thống tự động giáng cấp về Free.
"""
from datetime import date, timedelta
from repositories.database import db_session
from repositories.models import User

# Hằng số giới hạn — Admin có thể điều chỉnh sau này
FREE_CV_LIMIT = 3
FREE_MATCH_LIMIT = 3

# Các gói Pro (key, tên hiển thị, số tháng, giá VNĐ)
PRO_PLANS = [
    {"key": "1_month",  "name": "1 Tháng",  "months": 1,  "price": 49_000},
    {"key": "6_months", "name": "6 Tháng",  "months": 6,  "price": 249_000},
    {"key": "1_year",   "name": "1 Năm",    "months": 12, "price": 490_000},
]


def _check_pro_expiry(user: User):
    """Kiểm tra và tự động giáng cấp nếu gói Pro đã hết hạn."""
    if user.is_pro and user.pro_expiry_date:
        if user.pro_expiry_date < date.today():
            user.is_pro = False
            user.pro_expiry_date = None


def _reset_if_new_day(user: User):
    """Kiểm tra và reset bộ đếm nếu đã sang ngày mới."""
    today = date.today()
    if user.last_usage_reset is None or user.last_usage_reset < today:
        user.cv_ai_usage_count = 0
        user.match_ai_usage_count = 0
        user.last_usage_reset = today


def check_cv_quota(user_id: int) -> tuple[bool, str | None, dict | None]:
    """Kiểm tra xem người dùng còn lượt tạo CV bằng AI không.

    Returns:
        (True, None, quota_info) nếu còn lượt.
        (False, thông_báo_lỗi, quota_info) nếu hết lượt.
    """
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "Không tìm thấy người dùng.", None

        _check_pro_expiry(user)
        _reset_if_new_day(user)

        quota_info = {
            "is_pro": user.is_pro,
            "cv_used": user.cv_ai_usage_count,
            "cv_limit": FREE_CV_LIMIT,
        }

        # Tài khoản Pro → Cho qua luôn
        if user.is_pro:
            return True, None, quota_info

        # Tài khoản Free → Kiểm tra giới hạn
        if user.cv_ai_usage_count >= FREE_CV_LIMIT:
            db.commit()
            return False, (
                f"⚠️ Bạn đã dùng hết **{FREE_CV_LIMIT} lượt** tạo CV bằng AI hôm nay. "
                f"Hãy nâng cấp **Pro** để sử dụng không giới hạn!"
            ), quota_info

        db.commit()
        return True, None, quota_info


def increment_cv_usage(user_id: int):
    """Tăng bộ đếm lượt tạo CV lên 1 (gọi SAU KHI tạo CV thành công)."""
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user and not user.is_pro:
            _reset_if_new_day(user)
            user.cv_ai_usage_count = (user.cv_ai_usage_count or 0) + 1
            db.commit()


def check_match_quota(user_id: int) -> tuple[bool, str | None, dict | None]:
    """Kiểm tra xem người dùng còn lượt dùng AI phân tích Job không.

    Returns:
        (True, None, quota_info) nếu còn lượt.
        (False, thông_báo_lỗi, quota_info) nếu hết lượt.
    """
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "Không tìm thấy người dùng.", None

        _check_pro_expiry(user)
        _reset_if_new_day(user)

        quota_info = {
            "is_pro": user.is_pro,
            "match_used": user.match_ai_usage_count,
            "match_limit": FREE_MATCH_LIMIT,
        }

        if user.is_pro:
            return True, None, quota_info

        if user.match_ai_usage_count >= FREE_MATCH_LIMIT:
            db.commit()
            return False, (
                f"⚠️ Bạn đã dùng hết **{FREE_MATCH_LIMIT} lượt** phân tích AI hôm nay. "
                f"Hãy nâng cấp **Pro** để sử dụng không giới hạn!"
            ), quota_info

        db.commit()
        return True, None, quota_info


def increment_match_usage(user_id: int):
    """Tăng bộ đếm lượt dùng AI Match lên 1 (gọi SAU KHI phân tích thành công)."""
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user and not user.is_pro:
            _reset_if_new_day(user)
            user.match_ai_usage_count = (user.match_ai_usage_count or 0) + 1
            db.commit()


def get_user_quota(user_id: int) -> dict | None:
    """Lấy thông tin quota hiện tại của user (dùng cho Sidebar hiển thị)."""
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        _check_pro_expiry(user)
        _reset_if_new_day(user)
        db.commit()

        return {
            "is_pro": user.is_pro,
            "pro_expiry_date": str(user.pro_expiry_date) if user.pro_expiry_date else None,
            "cv_used": user.cv_ai_usage_count or 0,
            "cv_limit": FREE_CV_LIMIT,
            "match_used": user.match_ai_usage_count or 0,
            "match_limit": FREE_MATCH_LIMIT,
        }


def upgrade_to_pro(user_id: int, months: int = 1) -> tuple[bool, str | None]:
    """Nâng cấp tài khoản lên Pro với thời hạn cụ thể.

    Args:
        user_id: ID người dùng.
        months: Số tháng mua gói Pro (1, 6, hoặc 12).

    Returns:
        (True, None) nếu thành công.
        (False, thông_báo_lỗi) nếu thất bại.
    """
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "Không tìm thấy người dùng."

        today = date.today()

        # Nếu đang là Pro và chưa hết hạn → Cộng dồn thêm thời gian
        if user.is_pro and user.pro_expiry_date and user.pro_expiry_date >= today:
            base_date = user.pro_expiry_date
        else:
            base_date = today

        user.is_pro = True
        user.pro_expiry_date = base_date + timedelta(days=months * 30)
        db.commit()
        return True, None
