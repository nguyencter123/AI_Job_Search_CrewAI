# File: services/matching/engine.py
"""
Context (Ngữ cảnh) cho Strategy Design Pattern.

JobSearchEngine là "Bộ máy tìm kiếm" trung tâm. Nó KHÔNG tự tìm kiếm,
mà ỦY THÁC (delegate) toàn bộ công việc cho Strategy đang được gắn vào.

Đây chính là thành phần đặc trưng giúp phân biệt Strategy Pattern 
với Factory Pattern:
- Factory: Có Factory (nhà máy tạo đối tượng)
- Strategy: Có Context (ngữ cảnh chứa và sử dụng thuật toán)
"""
from services.matching.base import IMatchingStrategy


class JobSearchEngine:
    """Context — Bộ máy tìm kiếm việc làm.
    
    Sử dụng:
        engine = JobSearchEngine(BasicMatchingStrategy())
        results, error = engine.search(user_id, jobs, kw="Python")
        
        # Đổi thuật toán giữa chừng (Runtime switching)
        engine.set_strategy(AiMatchingStrategy())
        results, error = engine.search(user_id, jobs, kw="Python")
    """

    def __init__(self, strategy: IMatchingStrategy):
        """Khởi tạo Engine với một Strategy cụ thể.
        
        Args:
            strategy: Một đối tượng thuộc IMatchingStrategy 
                      (VD: BasicMatchingStrategy() hoặc AiMatchingStrategy()).
        """
        self._strategy = strategy

    @property
    def strategy(self) -> IMatchingStrategy:
        """Trả về Strategy hiện tại đang được sử dụng."""
        return self._strategy

    def set_strategy(self, strategy: IMatchingStrategy):
        """Thay đổi thuật toán tìm kiếm GIỮA CHỪNG lúc đang chạy (Runtime).
        
        Đây chính là sức mạnh cốt lõi của Strategy Pattern:
        Có thể đổi thuật toán mà KHÔNG cần khởi tạo lại Engine.
        """
        self._strategy = strategy

    def search(self, user_id: int, all_jobs: list, 
               search_kw: str = "", search_loc: str = "",
               search_salary: str = "Tất cả") -> tuple[list, str | None]:
        """Ủy thác toàn bộ việc tìm kiếm cho Strategy hiện tại.
        
        Returns:
            Tuple (danh_sách_kết_quả, thông_báo_lỗi_hoặc_None).
        """
        return self._strategy.match(
            user_id, all_jobs, search_kw, search_loc, search_salary
        )
