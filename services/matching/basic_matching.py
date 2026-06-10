# File: services/matching/basic_matching.py
"""
Concrete Strategy: Tìm kiếm Nhanh bằng Bộ lọc (Filter).
Logic được bưng nguyên từ hàm filter_jobs() trong job_matching_service.py.
"""
from services.matching.base import IMatchingStrategy


class BasicMatchingStrategy(IMatchingStrategy):
    """Chiến lược Tìm kiếm Nhanh — so sánh chuỗi ký tự đơn giản.
    
    Ưu điểm: Tốc độ xử lý gần như ngay lập tức (< 1ms).
    Nhược điểm: Không hiểu ngữ nghĩa, chỉ tìm khớp chữ.
    """

    def match(self, user_id: int, all_jobs: list,
              search_kw: str = "", search_loc: str = "",
              search_salary: str = "Tất cả") -> tuple[list, str | None]:
        """Lọc job bằng cách so sánh chuỗi ký tự với từ khóa, địa điểm, lương."""
        filtered = []
        for job in all_jobs:
            match_kw = True
            match_loc = True
            match_salary = True

            if search_kw:
                kw = search_kw.lower()
                search_area = f"{job['title']} {job['company']} {job['short_desc']}".lower()
                if kw not in search_area:
                    match_kw = False

            if search_loc and search_loc.strip() and search_loc.strip().lower() not in job["location"].lower():
                match_loc = False

            if search_salary != "Tất cả" and search_salary.lower() not in job["salary"].lower():
                match_salary = False

            if match_kw and match_loc and match_salary:
                filtered.append(job)

        return filtered, None
