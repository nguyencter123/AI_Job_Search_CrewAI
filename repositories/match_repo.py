# File: repositories/match_repo.py
"""Repository cho bảng UserJobMatch — Theo dõi job đã gửi email."""
from repositories.models import UserJobMatch


def get_emailed_job_ids(db, user_id: int) -> set[int]:
    """Lấy tập hợp job_id đã từng gửi email cho user này.
    
    Dùng để tránh gửi trùng lặp.
    """
    rows = (
        db.query(UserJobMatch.job_id)
        .filter(
            UserJobMatch.user_id == user_id,
            UserJobMatch.is_emailed == True,
        )
        .all()
    )
    return {r[0] for r in rows}


def save_match_records(db, user_id: int, matched_jobs: list[dict]):
    """Lưu kết quả match + đánh dấu đã gửi email.
    
    matched_jobs: [{"id": 1, "title": "...", "score": 85}, ...]
    """
    for job in matched_jobs:
        record = UserJobMatch(
            user_id=user_id,
            job_id=int(job["id"]),
            job_title=job.get("title", ""),
            match_score=float(job.get("score", 0)),
            is_emailed=True,
        )
        db.add(record)
    db.commit()
