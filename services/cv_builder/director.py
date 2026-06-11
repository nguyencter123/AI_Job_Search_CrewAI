# File: services/cv_builder/director.py
"""
Director (Đốc công) cho Builder Design Pattern.

CVDirector là "người điều phối" biết CHÍNH XÁC thứ tự xây dựng CV.
Nó ra lệnh cho Builder xây từng phần theo trình tự đúng.

Đây là thành phần ĐẶC TRƯNG giúp phân biệt Builder Pattern với các Pattern khác:
- Factory Pattern có Factory (nhà máy)
- Strategy Pattern có Context (ngữ cảnh)  
- Builder Pattern có Director (đốc công)

Director KHÔNG biết chi tiết xây như thế nào (màu gì, font gì).
Nó chỉ biết THỨ TỰ: Header → Mục tiêu → Kỹ năng → Kinh nghiệm → Học vấn.
"""
from services.cv_builder.base import ICVBuilder


class CVDirector:
    """Director — Đốc công điều phối quá trình xây dựng CV.
    
    Sử dụng:
        builder = StandardCVBuilder()
        director = CVDirector(builder)
        html = director.construct(user_data)
    """

    def __init__(self, builder: ICVBuilder):
        """Gắn một Builder cụ thể vào Director.
        
        Args:
            builder: Một đối tượng ICVBuilder 
                     (VD: StandardCVBuilder() hoặc ModernCVBuilder()).
        """
        self._builder = builder

    @property
    def builder(self) -> ICVBuilder:
        """Trả về Builder hiện tại."""
        return self._builder

    def set_builder(self, builder: ICVBuilder):
        """Đổi Builder giữa chừng (nếu muốn đổi mẫu CV)."""
        self._builder = builder

    def construct(self, cv_data: dict) -> str:
        """Điều phối xây dựng CV theo thứ tự chuẩn.
        
        Director ra lệnh cho Builder xây từng phần, theo đúng trình tự
        mà mẫu CV yêu cầu.
        
        Args:
            cv_data: Dictionary chứa dữ liệu CV, gồm các key:
                - full_name (str): Họ và tên
                - email (str): Email liên hệ
                - phone (str): Số điện thoại
                - avatar_base64 (str): Ảnh đại diện dạng base64
                - objective (str): Mục tiêu nghề nghiệp
                - skills (str): Kỹ năng
                - experience (str): Kinh nghiệm làm việc
                - education (str): Học vấn
                
        Returns:
            Chuỗi HTML hoàn chỉnh chứa CV (Product).
        """
        # Xóa trắng Builder trước khi xây mới
        self._builder.reset()

        # === RA LỆNH XÂY TỪNG PHẦN THEO THỨ TỰ ===
        
        # Bước 1: Xây Header (Ảnh + Tên + Liên hệ)
        self._builder.build_header(
            full_name=cv_data.get("full_name", ""),
            email=cv_data.get("email", ""),
            phone=cv_data.get("phone", ""),
            avatar_base64=cv_data.get("avatar_base64", ""),
        )

        # Bước 2: Xây Mục tiêu Nghề nghiệp
        self._builder.build_objective(
            cv_data.get("objective", "")
        )

        # Bước 3: Xây Kỹ năng
        self._builder.build_skills(
            cv_data.get("skills", "")
        )

        # Bước 4: Xây Kinh nghiệm Làm việc
        self._builder.build_experience(
            cv_data.get("experience", "")
        )

        # Bước 5: Xây Học vấn
        self._builder.build_education(
            cv_data.get("education", "")
        )

        # Lấy sản phẩm hoàn chỉnh (Product) từ Builder
        return self._builder.get_result()
