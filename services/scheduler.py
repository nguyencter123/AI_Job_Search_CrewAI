# File: services/scheduler.py
"""
Cấu hình APScheduler để chạy các tác vụ nền tự động (Cron Jobs).
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.notification_service import run_daily_notification

logger = logging.getLogger(__name__)

# Khởi tạo BackgroundScheduler (chạy ngầm không block Streamlit)
scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")

def _daily_job_wrapper():
    """Hàm bọc (wrapper) để chạy và log tiến trình."""
    logger.info("⏰ BẮT ĐẦU CHẠY TÁC VỤ 8H SÁNG: Gửi email thông báo việc làm...")
    try:
        result = run_daily_notification()
        logger.info(f"✅ HOÀN TẤT: {result.get('message')}")
    except Exception as e:
        logger.error(f"❌ LỖI trong quá trình gửi thông báo: {str(e)}")


def start_scheduler():
    """Khởi động bộ lập lịch nếu nó chưa chạy."""
    if not scheduler.running:
        # Lên lịch chạy vào đúng 8:00 sáng mỗi ngày
        scheduler.add_job(
            _daily_job_wrapper,
            trigger=CronTrigger(hour=8, minute=0),
            id="daily_email_job",
            name="Gửi email thông báo việc làm phù hợp hàng ngày",
            replace_existing=True
        )
        scheduler.start()
        logger.info("🚀 APScheduler đã khởi động. Lịch gửi email: 8:00 AM hàng ngày.")
    else:
        logger.info("ℹ️ APScheduler đang chạy, không cần khởi động lại.")
