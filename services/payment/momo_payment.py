# File: services/payment/momo_payment.py
"""
Concrete Strategy: Thanh toán qua Momo (Giả lập).
"""
from services.payment.base import IPaymentStrategy, PaymentResult


class MomoPayment(IPaymentStrategy):
    """Chiến lược thanh toán qua ví điện tử Momo."""

    def get_payment_info(self, amount: int) -> dict:
        """Trả về thông tin QR Momo để hiển thị."""
        return {
            "name": "Momo",
            "icon": "💜",
            "color": "#ae2070",
            "description": "Thanh toán qua ví điện tử Momo",
            "qr_data": f"momo://pay?amount={amount}&receiver=AI_JOB_SEARCH&note=NangCapPro",
            "instructions": [
                "1. Mở ứng dụng **Momo** trên điện thoại.",
                "2. Quét mã QR bên dưới hoặc chuyển khoản đến số **0901 234 567**.",
                f"3. Nhập số tiền: **{amount:,} VNĐ**.",
                "4. Nội dung chuyển khoản: **NangCapPro**.",
                "5. Bấm nút **'Tôi đã thanh toán'** bên dưới để hoàn tất.",
            ]
        }

    def confirm_payment(self, amount: int, **kwargs) -> PaymentResult:
        """Xác nhận thanh toán Momo (giả lập thành công)."""
        return PaymentResult(
            success=True,
            message=f"✅ Thanh toán {amount:,} VNĐ qua Momo thành công! Tài khoản đã được nâng cấp Pro."
        )
