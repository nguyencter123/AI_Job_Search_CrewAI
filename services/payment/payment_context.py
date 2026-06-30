# File: services/payment/payment_context.py
"""
Context class cho Strategy Pattern — Thanh toán.

PaymentContext đóng vai trò trung gian giữa View (giao diện) và
các Concrete Strategy (Momo, ZaloPay, VNPay). View chỉ cần gọi
PaymentContext mà không cần biết bên trong xử lý ra sao.

Sử dụng:
    context = PaymentContext("momo")
    info = context.get_payment_info(99000)
    result = context.confirm_payment(99000)
"""
from services.payment.base import IPaymentStrategy, PaymentResult
from services.payment.momo_payment import MomoPayment
from services.payment.zalopay_payment import ZaloPayPayment
from services.payment.vnpay_payment import VNPayPayment


# Giá gói Pro được quản lý trong ai_quota_service.PRO_PLANS


class PaymentContext:
    """Context — Điều phối viên thanh toán.

    Nhận tên phương thức từ giao diện, tự động chọn đúng Strategy
    và ủy quyền (delegate) toàn bộ công việc cho Strategy đó.

    Để mở rộng (ví dụ: thêm PayPal), chỉ cần:
    1. Tạo file paypal_payment.py chứa class PayPalPayment(IPaymentStrategy)
    2. Thêm "paypal": PayPalPayment vào _strategies
    3. Xong! Không cần sửa bất kỳ file nào khác.
    """

    _strategies: dict[str, type[IPaymentStrategy]] = {
        "momo": MomoPayment,
        "zalopay": ZaloPayPayment,
        "vnpay": VNPayPayment,
    }

    def __init__(self, method: str):
        """Khởi tạo Context với phương thức thanh toán được chọn.

        Args:
            method: Tên phương thức ("momo", "zalopay", "vnpay").

        Raises:
            ValueError: Nếu phương thức không được hỗ trợ.
        """
        strategy_class = self._strategies.get(method)
        if not strategy_class:
            raise ValueError(
                f"Phương thức thanh toán '{method}' không được hỗ trợ! "
                f"Các phương thức hợp lệ: {list(self._strategies.keys())}"
            )
        self._strategy: IPaymentStrategy = strategy_class()

    def get_payment_info(self, amount: int = 0) -> dict:
        """Lấy thông tin thanh toán từ Strategy hiện tại."""
        return self._strategy.get_payment_info(amount)

    def confirm_payment(self, amount: int = 0, **kwargs) -> PaymentResult:
        """Xác nhận thanh toán qua Strategy hiện tại."""
        return self._strategy.confirm_payment(amount, **kwargs)

    @staticmethod
    def get_available_methods() -> list[dict]:
        """Trả về danh sách các phương thức thanh toán có sẵn (dùng cho UI)."""
        methods = []
        for key, cls in PaymentContext._strategies.items():
            instance = cls()
            info = instance.get_payment_info(0)
            methods.append({
                "key": key,
                "name": info["name"],
                "icon": info["icon"],
                "description": info["description"],
            })
        return methods
