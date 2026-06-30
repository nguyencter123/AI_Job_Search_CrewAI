# File: services/job_matching_service.py
from __future__ import annotations

from repositories.database import db_session
from repositories.job_provider import get_all_jobs  # noqa: F401 — re-export cho Views
from repositories.user_repo import get_user_and_profile
from services.ai_service import analyze_and_rank_jobs


def filter_jobs(
    all_jobs: list,
    search_kw: str,
    search_loc: str,
    search_salary: str,
) -> list:
    """Lọc job theo từ khóa, địa điểm, loại tiền tệ trong chuỗi lương."""
    filtered: list = []
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
    return filtered


def merge_ai_ranking_into_jobs(filtered_jobs: list, ranked_data: list) -> list:
    """
    Ghép 
    
    """
    job_dict = {job["id"]: job for job in filtered_jobs}
    out: list = []
    seen: set = set()
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
        out.append(row)
        seen.add(jid)
    return out


def rank_user_jobs_against_list(user_id: int, filtered_jobs: list) -> tuple[list | None, str | None]:
    """
    Đọc profile từ DB, gọi AI chấm điểm danh sách job đã lọc.

    Returns:
        (danh_sách_job_đã_gắn_điểm, None) khi thành công
        (None, thông_báo_lỗi) khi thất bại
    """
    if not filtered_jobs:
        return None, "Không có công việc nào để phân tích."

    # Kiểm tra quota trước khi gọi AI
    from services.ai_quota_service import check_match_quota, increment_match_usage
    allowed, quota_error, _ = check_match_quota(user_id)
    if not allowed:
        return None, quota_error

    with db_session() as db:
        _user, profile = get_user_and_profile(db, user_id)

    if not profile or not (profile.skills and str(profile.skills).strip()):
        return None, "⚠️ Hãy cập nhật Hồ sơ (Kỹ năng, Kinh nghiệm) trước!"

    skills = profile.skills or ""
    experience = profile.experience_summary or ""

    ranked_data, error = analyze_and_rank_jobs(skills, experience, filtered_jobs)
    if error:
        return None, error

    if not ranked_data:
        return None, "AI không trả về dữ liệu xếp hạng."

    merged = merge_ai_ranking_into_jobs(filtered_jobs, ranked_data)
    if not merged:
        return None, "Không ghép được kết quả AI với danh sách công việc (kiểm tra id job)."

    # Phân tích thành công → Tăng bộ đếm
    increment_match_usage(user_id)

    return merged, None
