# File: services/matching/ai_matching.py
"""
Concrete Strategy: Tìm kiếm Sâu bằng AI (Gemini).
Logic được bưng từ hàm rank_user_jobs_against_list() trong job_matching_service.py.

Luồng hoạt động:
1. Lọc sơ bộ bằng bộ lọc (giống BasicMatching) để giảm số lượng job gửi lên AI.
2. Đọc Profile (skills, experience) của ứng viên từ Database.
3. Gửi danh sách job đã lọc + Profile lên API Gemini để chấm điểm.
4. Ghép điểm AI vào danh sách job và trả về (sắp xếp từ cao -> thấp).
"""
from services.matching.base import IMatchingStrategy
from services.matching.basic_matching import BasicMatchingStrategy
from repositories.database import db_session
from repositories.user_repo import get_user_and_profile
from services.ai_service import analyze_and_rank_jobs


class AiMatchingStrategy(IMatchingStrategy):
    """Chiến lược Tìm kiếm Sâu — dùng AI phân tích ngữ nghĩa CV vs JD.
    
    Ưu điểm: Thông minh, hiểu ngữ nghĩa (VD: "Backend" ≈ "Server-side Developer").
    Nhược điểm: Chậm (3-5 giây), phụ thuộc vào API bên ngoài.
    """

    def match(self, user_id: int, all_jobs: list,
              search_kw: str = "", search_loc: str = "",
              search_salary: str = "Tất cả") -> tuple[list, str | None]:
        """Lọc sơ bộ bằng bộ lọc, sau đó gọi AI chấm điểm từng job."""
        
        # Bước 1: Lọc sơ bộ trước (tái sử dụng BasicMatchingStrategy)
        basic = BasicMatchingStrategy()
        filtered_jobs, _ = basic.match(user_id, all_jobs, search_kw, search_loc, search_salary)
        
        if not filtered_jobs:
            return [], "Không có công việc nào phù hợp với bộ lọc để phân tích."

        # Kiểm tra quota trước khi gọi AI
        from services.ai_quota_service import check_match_quota, increment_match_usage
        allowed, quota_error, _ = check_match_quota(user_id)
        if not allowed:
            return [], quota_error

        # Bước 2: Đọc Profile ứng viên từ Database
        with db_session() as db:
            _user, profile = get_user_and_profile(db, user_id)

        if not profile or not (profile.skills and str(profile.skills).strip()):
            return [], "⚠️ Hãy cập nhật Hồ sơ (Kỹ năng, Kinh nghiệm) trước!"

        skills = profile.skills or ""
        experience = profile.experience_summary or ""

        # Bước 3: Gửi lên API Gemini để chấm điểm
        ranked_data, error = analyze_and_rank_jobs(skills, experience, filtered_jobs)
        if error:
            return [], error

        if not ranked_data:
            return [], "AI không trả về dữ liệu xếp hạng."

        # Bước 4: Ghép điểm AI vào danh sách job
        job_dict = {job["id"]: job for job in filtered_jobs}
        merged = []
        seen = set()
        for item in ranked_data:
            jid = item.get("id")
            if not jid or jid in seen:
                continue
            src = job_dict.get(jid)
            if not src:
                continue
            row = dict(src)
            row["ai_score"] = item.get("score", 0)
            row["ai_reason"] = item.get("reason", "")
            merged.append(row)
            seen.add(jid)

        if not merged:
            return [], "Không ghép được kết quả AI với danh sách công việc."

        # Phân tích thành công → Tăng bộ đếm
        increment_match_usage(user_id)

        return merged, None
