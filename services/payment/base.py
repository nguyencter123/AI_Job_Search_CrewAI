# File: services/payment/base.py
"""
Interface (Khuôn mẫu) cho Strategy Design Pattern — Thanh toán.

Mọi phương thức thanh toán (Momo, ZaloPay, VNPay) đều PHẢI kế thừa
IPaymentStrategy và triển khai đầy đủ các phương thức bên dưới.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentResult:
    """Kết quả trả về thống nhất cho MỌI phương thức thanh toán.

    Attributes:
        success: True nếu thanh toán thành công.
        message: Thông báo cho người dùng.
        qr_image_path: Đường dẫn ảnh QR Code (nếu có).
    """
    success: bool = False
    message: str = ""
    qr_image_path: str = ""


class IPaymentStrategy(ABC):
    """Abstract Base Class: Hợp đồng bắt buộc cho mọi cổng thanh toán.

    Mỗi cổng thanh toán phải triển khai 2 phương thức:
    - get_payment_info(): Trả về thông tin hiển thị (tên, QR, hướng dẫn).
    - confirm_payment(): Xác nhận và xử lý thanh toán.
    """

    @abstractmethod
    def get_payment_info(self, amount: int) -> dict:
        """Trả về thông tin thanh toán để hiển thị trên giao diện.

        Args:
            amount: Số tiền cần thanh toán (VNĐ).

        Returns:
            Dict chứa: name, description, qr_data, instructions.
        """
        pass

    @abstractmethod
    def confirm_payment(self, amount: int, **kwargs) -> PaymentResult:
        """Xác nhận thanh toán (giả lập).

        Args:
            amount: Số tiền thanh toán.
            **kwargs: Các tham số bổ sung tùy cổng.

        Returns:
            PaymentResult chứa kết quả thanh toán.
        """
        pass
