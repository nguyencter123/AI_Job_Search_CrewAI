# File: services/notification/email_observer.py
"""
Concrete Observer: Gửi Email thông báo việc làm phù hợp.

Đây là "Người theo dõi" cụ thể trong Observer Pattern.
Khi Subject gọi update(), Observer này sẽ:
1. Lọc job CHƯA gửi cho user (tránh trùng lặp)
2. Gọi AI chấm điểm (chỉ giữ score >= 70%)
3. Giới hạn tối đa 2 job/email (tiết kiệm API quota)
4. Gửi email HTML đẹp qua SMTP
5. Lưu lại vào DB (đánh dấu is_emailed = True)
"""
import logging

from services.notification.base import IJobObserver
from services.email_service import send_email, build_job_notification_html
from services.ai_service import analyze_and_rank_jobs
from repositories.database import db_session
from repositories.match_repo import get_emailed_job_ids, save_match_records

logger = logging.getLogger(__name__)

# ═══ Cấu hình ═══
SCORE_THRESHOLD = 70   # Chỉ gửi job có điểm >= 70%
MAX_JOBS_PER_EMAIL = 2  # Tối đa 2 job/email (tiết kiệm API free)


class EmailNotificationObserver(IJobObserver):
    """Concrete Observer — Gửi email thông báo việc làm phù hợp."""

    def update(self, new_jobs: list[dict], eligible_users: list) -> dict:
        """Xử lý gửi email cho tất cả user đủ điều kiện.
        
        Args:
            new_jobs: Danh sách tất cả job mới
            eligible_users: list of (User, UserProfile) tuples
            
        Returns:
            {"sent": số email đã gửi, "skipped": số user bỏ qua, "errors": list lỗi}
        """
        sent_count = 0
        skipped_count = 0
        errors = []

        for user, profile in eligible_users:
            try:
                result = self._process_one_user(user, profile, new_jobs)
                if result == "sent":
                    sent_count += 1
                elif result == "skipped":
                    skipped_count += 1
            except Exception as e:
                error_msg = f"Lỗi xử lý user {user.email}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        return {
            "sent": sent_count,
            "skipped": skipped_count,
            "errors": errors,
        }

    def _process_one_user(self, user, profile, all_new_jobs: list[dict]) -> str:
        """Xử lý gửi email cho 1 user.
        
        Returns: "sent" | "skipped"
        """
        # Bước 1: Lọc job chưa từng gửi cho user này
        with db_session() as db:
            emailed_ids = get_emailed_job_ids(db, user.id)

        unsent_jobs = [j for j in all_new_jobs if int(j["id"]) not in emailed_ids]
        if not unsent_jobs:
            return "skipped"

        # Đề phòng quá tải API Gemini (vì có tới 161 jobs), ta chỉ lấy ngẫu nhiên tối đa 15 jobs MỚI NHẤT
        import random
        if len(unsent_jobs) > 15:
            unsent_jobs = random.sample(unsent_jobs, 15)

        # 2. Chấm điểm bằng AI
        skills = profile.skills or ""
        experience = profile.experience_summary or ""

        ranked_data, ai_error = analyze_and_rank_jobs(skills, experience, unsent_jobs)

        if ai_error or not ranked_data:
            logger.warning(f"AI error cho user {user.email}: {ai_error}")
            return "skipped"

        # Bước 3: Lọc score >= 70% + giới hạn 2 job
        matched_jobs = [
            r for r in ranked_data
            if r.get("score", 0) >= SCORE_THRESHOLD
        ][:MAX_JOBS_PER_EMAIL]

        if not matched_jobs:
            return "skipped"  # Không có job nào phù hợp

        # Bước 4: Bổ sung thông tin job (title, company, salary) vào kết quả AI
        job_map = {str(j["id"]): j for j in unsent_jobs}
        for m in matched_jobs:
            job_info = job_map.get(str(m["id"]), {})
            m["title"] = job_info.get("title", m.get("title", "N/A"))
            m["company"] = job_info.get("company", "")
            m["salary"] = job_info.get("salary", "Thỏa thuận")

        # Bước 5: Tạo email HTML + gửi
        user_name = profile.full_name or user.email
        html = build_job_notification_html(user_name, matched_jobs)
        subject = f"💼 AI Job Hub: {len(matched_jobs)} việc làm mới phù hợp với bạn!"

        ok, err = send_email(user.email, subject, html)

        if not ok:
            logger.error(f"Gửi email thất bại cho {user.email}: {err}")
            return "skipped"

        # Bước 6: Lưu vào DB — đánh dấu đã gửi
        with db_session() as db:
            save_match_records(db, user.id, matched_jobs)

        logger.info(f"✅ Đã gửi {len(matched_jobs)} job cho {user.email}")
        return "sent"
