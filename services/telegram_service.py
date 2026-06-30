# File: services/telegram_service.py
"""
Dịch vụ gửi tin nhắn qua Telegram Bot API.
"""
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

def send_telegram_message(chat_id: str, text: str) -> tuple[bool, str | None]:
    """
    Gửi tin nhắn văn bản (hỗ trợ Markdown) qua Telegram Bot.
    
    Args:
        chat_id: ID của người nhận (có được qua userinfobot)
        text: Nội dung tin nhắn (chuẩn MarkdownV2 hoặc HTML)
    Returns:
        (True, None) nếu thành công
        (False, error_msg) nếu thất bại
    """
    if not TELEGRAM_BOT_TOKEN:
        return False, "Chưa cấu hình TELEGRAM_BOT_TOKEN trong .env"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get("ok"):
            return True, None
        else:
            err_desc = data.get("description", "Unknown error")
            return False, f"Lỗi từ Telegram API: {err_desc}"
            
    except Exception as e:
        logger.error(f"Lỗi khi gọi Telegram API: {e}")
        return False, str(e)
