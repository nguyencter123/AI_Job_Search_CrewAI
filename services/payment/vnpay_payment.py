# File: services/payment/vnpay_payment.py
"""
Concrete Strategy: Thanh toán qua VNPay (Giả lập).
"""
from services.payment.base import IPaymentStrategy, PaymentResult


class VNPayPayment(IPaymentStrategy):
    """Chiến lược thanh toán qua cổng VNPay (Ngân hàng nội địa)."""

    def get_payment_info(self, amount: int) -> dict:
        """Trả về thông tin QR VNPay để hiển thị."""
        return {
            "name": "VNPay",
            "icon": "🏦",
            "color": "#e41e2e",
            "description": "Thanh toán qua cổng VNPay (Ngân hàng nội địa)",
            "qr_data": f"vnpay://pay?amount={amount}&merchant=AI_JOB_SEARCH&note=NangCapPro",
            "instructions": [
                "1. Mở ứng dụng **Ngân hàng** trên điện thoại (Vietcombank, BIDV, Techcombank...).",
                "2. Chọn **'Quét mã VNPay'** và quét mã bên dưới.",
                f"3. Xác nhận số tiền: **{amount:,} VNĐ**.",
                "4. Nội dung chuyển khoản: **NangCapPro**.",
                "5. Bấm nút **'Tôi đã thanh toán'** bên dưới để hoàn tất.",
            ]
        }

    def confirm_payment(self, amount: int, **kwargs) -> PaymentResult:
        """Xác nhận thanh toán VNPay (giả lập thành công)."""
        return PaymentResult(
            success=True,
            message=f"✅ Thanh toán {amount:,} VNĐ qua VNPay thành công! Tài khoản đã được nâng cấp Pro."
        )
