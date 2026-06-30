# File: services/payment/zalopay_payment.py
"""
Concrete Strategy: Thanh toán qua ZaloPay (Giả lập).
"""
from services.payment.base import IPaymentStrategy, PaymentResult


class ZaloPayPayment(IPaymentStrategy):
    """Chiến lược thanh toán qua ví điện tử ZaloPay."""

    def get_payment_info(self, amount: int) -> dict:
        """Trả về thông tin QR ZaloPay để hiển thị."""
        return {
            "name": "ZaloPay",
            "icon": "💙",
            "color": "#0068ff",
            "description": "Thanh toán qua ví điện tử ZaloPay",
            "qr_data": f"zalopay://pay?amount={amount}&receiver=AI_JOB_SEARCH&note=NangCapPro",
            "instructions": [
                "1. Mở ứng dụng **ZaloPay** trên điện thoại.",
                "2. Chọn **'Quét mã QR'** và quét mã bên dưới.",
                f"3. Xác nhận số tiền: **{amount:,} VNĐ**.",
                "4. Nội dung chuyển khoản: **NangCapPro**.",
                "5. Bấm nút **'Tôi đã thanh toán'** bên dưới để hoàn tất.",
            ]
        }

    def confirm_payment(self, amount: int, **kwargs) -> PaymentResult:
        """Xác nhận thanh toán ZaloPay (giả lập thành công)."""
        return PaymentResult(
            success=True,
            message=f"✅ Thanh toán {amount:,} VNĐ qua ZaloPay thành công! Tài khoản đã được nâng cấp Pro."
        )
