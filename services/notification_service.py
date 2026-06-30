# File: services/notification_service.py
"""
Notification Service — Điều phối gửi thông báo (Orchestrator).

Hàm chính: run_daily_notification()
1. Tạo JobSubject (Subject trong Observer Pattern)
2. Attach EmailNotificationObserver (Concrete Observer)
3. Lấy danh sách job + user đủ điều kiện
4. Gọi subject.notify_all() → Observer tự xử lý
"""
import logging

from services.notification.base import JobSubject
from services.notification.email_observer import EmailNotificationObserver
from services.notification.telegram_observer import TelegramNotificationObserver
from repositories.database import db_session
from repositories.user_repo import get_users_for_notification
from services.job_matching_service import get_all_jobs

logger = logging.getLogger(__name__)


def run_daily_notification(channel: str = "all") -> dict:
    """Chạy gửi thông báo công việc mới cho tất cả user đủ điều kiện.
    
    Luồng Observer Pattern:
    1. Tạo Subject
    2. Attach Observer(s) dựa theo tham số channel
    3. Lấy dữ liệu (jobs + users)
    4. Subject.notify_all() → Các Observer tự xử lý
    
    Args:
        channel: "all", "email", hoặc "telegram"
        
    Returns:
        dict: {"total_users": N, "total_jobs": N, "results": [...]}
    """
    # ── Bước 1: Lấy danh sách job hiện có ──
    all_jobs = get_all_jobs()
    if not all_jobs:
        return {
            "total_users": 0,
            "total_jobs": 0,
            "results": [],
            "message": "Không có công việc nào trong hệ thống.",
        }

    # ── Bước 2: Lấy danh sách user đủ điều kiện ──
    with db_session() as db:
        eligible_users = get_users_for_notification(db)
        # Detach từ session để dùng bên ngoài
        user_data = []
        for user, profile in eligible_users:
            db.expunge(user)
            db.expunge(profile)
            user_data.append((user, profile))

    if not user_data:
        return {
            "total_users": 0,
            "total_jobs": len(all_jobs),
            "results": [],
            "message": "Không có user nào đủ điều kiện nhận thông báo.",
        }

    # ── Bước 3: Tạo Subject + Attach Observer (Observer Pattern) ──
    subject = JobSubject()
    
    if channel in ["all", "email"]:
        subject.attach(EmailNotificationObserver())
        
    if channel in ["all", "telegram"]:
        subject.attach(TelegramNotificationObserver())

    # ── Bước 4: Phát thông báo cho tất cả Observer ──
    logger.info(f"🚀 Bắt đầu gửi thông báo: {len(all_jobs)} jobs → {len(user_data)} users")
    results = subject.notify_all(all_jobs, user_data)

    total_sent = sum(r.get("sent", 0) for r in results)
    total_skipped = sum(r.get("skipped", 0) for r in results)

    return {
        "total_users": len(user_data),
        "total_jobs": len(all_jobs),
        "total_sent": total_sent,
        "total_skipped": total_skipped,
        "results": results,
        "message": f"Đã xử lý thông báo thành công. Tổng lượt gửi: {total_sent}, bỏ qua: {total_skipped}.",
    }
