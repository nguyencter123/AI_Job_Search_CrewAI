# File: services/cv_builder/base.py
"""
Builder Interface (Khuôn mẫu) cho Builder Design Pattern.

Mọi kiểu CV (StandardCV, ModernCV, ...) đều PHẢI kế thừa ICVBuilder
và triển khai đầy đủ các bước xây dựng CV.

Vai trò trong Builder Pattern:
- ICVBuilder = Abstract Builder (Khuôn mẫu thợ xây)
- Các phương thức = Các bước xây dựng bắt buộc
"""
from abc import ABC, abstractmethod


class ICVBuilder(ABC):
    """Abstract Builder: Hợp đồng bắt buộc cho mọi loại CV Builder.
    
    Mỗi phương thức tương ứng với một PHẦN (section) của CV.
    Builder phải triển khai tất cả các phần này.
    """

    @abstractmethod
    def reset(self):
        """Xóa trắng CV, chuẩn bị xây mới từ đầu."""
        pass

    @abstractmethod
    def build_header(self, full_name: str, email: str = "", 
                     phone: str = "", avatar_base64: str = ""):
        """Xây phần Header: Ảnh đại diện + Họ tên + Thông tin liên hệ."""
        pass

    @abstractmethod
    def build_objective(self, objective_text: str):
        """Xây phần Mục tiêu Nghề nghiệp."""
        pass

    @abstractmethod
    def build_skills(self, skills_text: str):
        """Xây phần Kỹ năng (dạng danh sách bullet points)."""
        pass

    @abstractmethod
    def build_experience(self, experience_text: str):
        """Xây phần Kinh nghiệm Làm việc."""
        pass

    @abstractmethod
    def build_education(self, education_text: str):
        """Xây phần Học vấn."""
        pass

    @abstractmethod
    def get_result(self) -> str:
        """Trả về sản phẩm CV hoàn chỉnh (Product) dưới dạng HTML."""
        pass
