# File: services/notification/telegram_observer.py
"""
Concrete Observer: Gửi Telegram thông báo việc làm phù hợp.

Observer này sẽ:
1. Chỉ xử lý các user có điền telegram_chat_id
2. Lọc job CHƯA gửi (dựa trên is_emailed - ta dùng chung bảng user_job_matches)
3. Gọi AI chấm điểm (score >= 70%)
4. Gửi tin nhắn qua Telegram Bot
5. Lưu lại DB
"""
import logging

from services.notification.base import IJobObserver
from services.telegram_service import send_telegram_message
from services.ai_service import analyze_and_rank_jobs
from repositories.database import db_session
from repositories.match_repo import get_emailed_job_ids, save_match_records

logger = logging.getLogger(__name__)

SCORE_THRESHOLD = 70
MAX_JOBS_PER_MSG = 2


class TelegramNotificationObserver(IJobObserver):
    """Concrete Observer — Gửi tin nhắn Telegram cho việc làm phù hợp."""

    def update(self, new_jobs: list[dict], eligible_users: list) -> dict:
        sent_count = 0
        skipped_count = 0
        errors = []

        for user, profile in eligible_users:
            if not profile.receive_daily_telegram or not profile.telegram_chat_id:
                # User này không dùng Telegram hoặc đã tắt
                continue

            try:
                result = self._process_one_user(user, profile, new_jobs)
                if result == "sent":
                    sent_count += 1
                elif result == "skipped":
                    skipped_count += 1
            except Exception as e:
                error_msg = f"Lỗi xử lý Telegram cho user {user.email}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        return {
            "sent": sent_count,
            "skipped": skipped_count,
            "errors": errors,
        }

    def _process_one_user(self, user, profile, all_new_jobs: list[dict]) -> str:
        # 1. Lọc job chưa gửi
        with db_session() as db:
            emailed_ids = get_emailed_job_ids(db, user.id)

        unsent_jobs = [j for j in all_new_jobs if int(j["id"]) not in emailed_ids]
        if not unsent_jobs:
            return "skipped"

        # Đề phòng quá tải API Gemini, ta lấy ngẫu nhiên 15 jobs
        import random
        if len(unsent_jobs) > 15:
            unsent_jobs = random.sample(unsent_jobs, 15)

        # 2. Chấm điểm bằng AI
        skills = profile.skills or ""
        experience = profile.experience_summary or ""

        ranked_data, ai_error = analyze_and_rank_jobs(skills, experience, unsent_jobs)
        if ai_error or not ranked_data:
            return "skipped"

        # 3. Lọc & Giới hạn
        matched_jobs = [
            r for r in ranked_data
            if r.get("score", 0) >= SCORE_THRESHOLD
        ][:MAX_JOBS_PER_MSG]

        if not matched_jobs:
            return "skipped"

        # 4. Lấy thông tin job
        job_map = {str(j["id"]): j for j in unsent_jobs}
        
        # 5. Format tin nhắn Telegram HTML
        msg_lines = [
            f"🎯 <b>AI Job Hub tìm thấy {len(matched_jobs)} công việc mới cho bạn!</b>\n"
        ]
        
        for m in matched_jobs:
            job_info = job_map.get(str(m["id"]), {})
            title = job_info.get("title", m.get("title", "N/A"))
            company = job_info.get("company", "")
            salary = job_info.get("salary", "Thỏa thuận")
            score = m.get("score", 0)
            
            msg_lines.append(f"💼 <b>{title}</b>")
            msg_lines.append(f"🏢 Công ty: {company}")
            msg_lines.append(f"💰 Lương: {salary}")
            msg_lines.append(f"⭐ Phù hợp: {score}%")
            msg_lines.append(f"🔗 <a href='http://localhost:8501'>Xem chi tiết trên Web</a>\n")

        html_text = "\n".join(msg_lines)

        # 6. Gửi Telegram
        ok, err = send_telegram_message(profile.telegram_chat_id, html_text)
        if not ok:
            logger.error(f"Gửi Telegram thất bại cho {profile.telegram_chat_id}: {err}")
            return "skipped"

        # 7. Lưu DB (Dùng chung với Email để tránh gửi trùng ở cả 2 kênh nếu user bật cả 2)
        with db_session() as db:
            save_match_records(db, user.id, matched_jobs)

        logger.info(f"✅ Đã gửi {len(matched_jobs)} job qua Telegram cho {user.email}")
        return "sent"
