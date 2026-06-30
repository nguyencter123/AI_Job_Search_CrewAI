# File: services/email_service.py
"""
Dịch vụ gửi Email qua SMTP (Gmail).

Cung cấp:
- send_email(): Gửi 1 email HTML
- build_job_notification_html(): Tạo template email thông báo việc làm
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)


def send_email(to_email: str, subject: str, html_content: str) -> tuple[bool, str | None]:
    """Gửi email HTML qua SMTP.
    
    Returns:
        (True, None) nếu thành công
        (False, error_message) nếu lỗi
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        return False, "Chưa cấu hình SMTP (thiếu SMTP_USER/SMTP_PASSWORD trong .env)"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = to_email
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())

        return True, None
    except smtplib.SMTPAuthenticationError:
        return False, "Sai mật khẩu SMTP hoặc chưa bật App Password trên Gmail"
    except Exception as e:
        return False, f"Lỗi gửi email: {str(e)}"


def build_job_notification_html(user_name: str, matched_jobs: list[dict]) -> str:
    """Tạo template HTML email thông báo việc làm phù hợp.
    
    matched_jobs: [{"title": "...", "company": "...", "score": 85, "reason": "...", "salary": "..."}, ...]
    """
    job_cards = ""
    for job in matched_jobs:
        score = int(job.get("score", 0))
        score_color = "#16a34a" if score >= 80 else "#ca8a04"
        
        job_cards += f"""
        <div style="background: #f8f9fa; border-left: 4px solid {score_color}; 
                    padding: 16px; margin-bottom: 12px; border-radius: 0 8px 8px 0;">
            <div style="font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 4px;">
                {job.get('title', 'N/A')}
            </div>
            <div style="font-size: 13px; color: #555; margin-bottom: 6px;">
                🏢 {job.get('company', '')} &nbsp;|&nbsp; 💰 {job.get('salary', 'Thỏa thuận')}
            </div>
            <div style="font-size: 13px; color: {score_color}; font-weight: 500;">
                🎯 Độ phù hợp: {score}% — {job.get('reason', '')}
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head><meta charset="UTF-8"></head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f0f0f0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; 
                    box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0284c7, #0ea5e9); 
                        padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 22px;">💼 AI Job Hub</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0; font-size: 14px;">
                    Thông báo việc làm phù hợp với bạn
                </p>
            </div>
            
            <!-- Body -->
            <div style="padding: 24px;">
                <p style="font-size: 15px; color: #333;">
                    Xin chào <strong>{user_name}</strong>,
                </p>
                <p style="font-size: 14px; color: #555; line-height: 1.6;">
                    AI của chúng tôi đã phân tích hồ sơ của bạn và tìm thấy 
                    <strong>{len(matched_jobs)} công việc</strong> phù hợp với kỹ năng của bạn:
                </p>
                
                {job_cards}
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="http://localhost:8501" 
                       style="display: inline-block; background: #0284c7; color: white; 
                              padding: 12px 28px; border-radius: 8px; text-decoration: none;
                              font-weight: 600; font-size: 14px;">
                        🔍 Xem chi tiết trên AI Job Hub
                    </a>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f8f9fa; padding: 16px; text-align: center; 
                        font-size: 12px; color: #999;">
                Bạn nhận email này vì đã bật thông báo việc làm trên AI Job Hub.<br>
                Để tắt, vào Hồ sơ cá nhân → bỏ chọn "Nhận email thông báo".
            </div>
        </div>
    </body>
    </html>
    """
