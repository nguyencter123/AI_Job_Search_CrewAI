# File: services/matching/base.py
"""
Interface (Khuôn mẫu) cho Strategy Design Pattern.
Mọi thuật toán tìm kiếm việc làm đều PHẢI kế thừa IMatchingStrategy
và triển khai hàm match().
"""
from abc import ABC, abstractmethod


class IMatchingStrategy(ABC):
    """Abstract Base Class: Hợp đồng bắt buộc cho mọi chiến lược tìm kiếm.
    
    Bất kỳ class nào kế thừa IMatchingStrategy mà KHÔNG viết hàm match()
    sẽ bị Python báo lỗi TypeError ngay khi khởi tạo.
    """

    @abstractmethod
    def match(self, user_id: int, all_jobs: list, 
              search_kw: str = "", search_loc: str = "", 
              search_salary: str = "Tất cả") -> tuple[list, str | None]:
        """Tìm kiếm và trả về danh sách công việc phù hợp.
        
        Args:
            user_id: ID người dùng hiện tại.
            all_jobs: Toàn bộ danh sách công việc từ Database.
            search_kw: Từ khóa tìm kiếm (VD: "Python", "React").
            search_loc: Địa điểm (VD: "Hà Nội", "Remote").
            search_salary: Bộ lọc lương (VD: "Tất cả", "VNĐ", "USD").
            
        Returns:
            Tuple (danh_sách_kết_quả, thông_báo_lỗi_hoặc_None).
        """
        pass
