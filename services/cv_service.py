# File: services/cv_service.py
"""
Facade cho chức năng Tạo CV.

File này đóng vai trò Facade (Mặt tiền), kết nối:
1. Database → Lấy thông tin Profile của ứng viên
2. AI Gemini → Viết lại nội dung CV cho chuyên nghiệp
3. Builder Pattern → Xây dựng CV HTML theo mẫu
"""
import os
import json
import base64

import google.generativeai as genai
from dotenv import load_dotenv

from repositories.database import db_session
from repositories.user_repo import get_user_and_profile
from services.cv_builder.standard_builder import StandardCVBuilder
from services.cv_builder.director import CVDirector

load_dotenv()


def _generate_cv_content_with_ai(skills: str, experience: str, jd_text: str) -> tuple[dict | None, str | None]:
    """Gọi AI Gemini để viết nội dung CV chuyên nghiệp.
    
    AI sẽ dựa vào kỹ năng, kinh nghiệm của ứng viên + JD công việc
    để viết ra các phần: Mục tiêu, Kỹ năng, Kinh nghiệm, Học vấn.
    
    Returns:
        (dict_nội_dung, None) khi thành công
        (None, thông_báo_lỗi) khi thất bại
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "Điền_Key_Của_Bạn_Vào_Đây":
        return None, "Chưa cấu hình GEMINI_API_KEY trong file .env"

    genai.configure(api_key=api_key)

    prompt = f"""
Bạn là chuyên gia tư vấn nghề nghiệp hàng đầu Việt Nam. Hãy viết nội dung CV chuyên nghiệp bằng TIẾNG VIỆT dựa trên thông tin sau:

[KỸ NĂNG CỦA ỨNG VIÊN]
{skills}

[KINH NGHIỆM CỦA ỨNG VIÊN]
{experience}

[MÔ TẢ CÔNG VIỆC ĐANG ỨNG TUYỂN]
{jd_text}

Hãy trả về DUY NHẤT một JSON object (không markdown, không ```) có cấu trúc:
{{
    "objective": "Đoạn văn 2-3 câu về mục tiêu nghề nghiệp, tập trung vào giá trị mà ứng viên mang lại cho nhà tuyển dụng",
    "skills": "Danh sách kỹ năng ngắn gọn, mỗi kỹ năng cách nhau bởi dấu phẩy. Ưu tiên kỹ năng liên quan đến JD",
    "experience": "Kinh nghiệm làm việc. Mỗi vị trí ghi trên 1 dòng bắt đầu bằng **Tên vị trí - Công ty**, các chi tiết bắt đầu bằng dấu -",
    "education": "Thông tin học vấn. Mỗi trường ghi trên 1 dòng bắt đầu bằng **Tên trường**, chi tiết bắt đầu bằng dấu -"
}}

LƯU Ý: 
- Viết tự nhiên, chuyên nghiệp, KHÔNG bịa đặt thông tin không có trong dữ liệu gốc.
- Nếu không có thông tin về học vấn, hãy ghi "Đang cập nhật".
- Kỹ năng phải liệt kê dạng ngắn gọn (VD: "Python, React, Docker, Quản lý dự án").
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        raw = (response.text or "").strip()
        
        # Xóa code fences nếu có
        if "```" in raw:
            import re
            parts = re.split(r"```(?:json)?\s*", raw, flags=re.IGNORECASE)
            if len(parts) >= 2:
                raw = parts[1].split("```", 1)[0].strip()
        
        data = json.loads(raw)
        return data, None

    except json.JSONDecodeError as e:
        return None, f"AI trả về dữ liệu không hợp lệ: {e}"
    except Exception as e:
        return None, f"Lỗi khi gọi AI: {e}"


def generate_cv(user_id: int, jd_text: str = "", use_ai: bool = True) -> tuple[str | None, str | None]:
    """Tạo CV hoàn chỉnh cho ứng viên.
    
    Luồng hoạt động:
    1. Đọc Profile từ Database
    2. (Tùy chọn) Gọi AI viết nội dung chuyên nghiệp
    3. Dùng Builder Pattern xây CV HTML
    
    Args:
        user_id: ID ứng viên
        jd_text: Mô tả công việc (JD) đang ứng tuyển
        use_ai: True = dùng AI viết nội dung, False = dùng dữ liệu thô từ Profile
        
    Returns:
        (html_cv, None) khi thành công
        (None, thông_báo_lỗi) khi thất bại
    """
    # === Bước 1: Đọc Profile từ Database ===
    with db_session() as db:
        user, profile = get_user_and_profile(db, user_id)

    if not user or not profile:
        return None, "Không tìm thấy hồ sơ. Hãy cập nhật Profile trước!"

    full_name = profile.full_name or "Ứng viên"
    email = user.email or ""
    phone = user.phone_number or ""
    skills = profile.skills or ""
    experience = profile.experience_summary or ""

    if not skills.strip() and not experience.strip():
        return None, "⚠️ Hồ sơ trống! Hãy cập nhật Kỹ năng và Kinh nghiệm trước khi tạo CV."

    # Chuyển avatar sang base64 (nếu có)
    avatar_base64 = ""
    if profile.avatar_data:
        avatar_base64 = base64.b64encode(profile.avatar_data).decode("utf-8")

    # === Bước 2: Chuẩn bị dữ liệu CV ===
    if use_ai and jd_text.strip():
        # Gọi AI viết nội dung chuyên nghiệp
        ai_content, error = _generate_cv_content_with_ai(skills, experience, jd_text)
        if error:
            return None, error
        
        cv_data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "avatar_base64": avatar_base64,
            "objective": ai_content.get("objective", ""),
            "skills": ai_content.get("skills", skills),
            "experience": ai_content.get("experience", experience),
            "education": ai_content.get("education", "Đang cập nhật"),
        }
    else:
        # Dùng dữ liệu thô từ Profile (không gọi AI)
        cv_data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "avatar_base64": avatar_base64,
            "objective": "",
            "skills": skills,
            "experience": experience,
            "education": "",
        }

    # === Bước 3: Dùng Builder Pattern xây CV ===
    # Tạo Builder (Thợ xây) theo mẫu Standard
    builder = StandardCVBuilder()
    
    # Tạo Director (Đốc công) và gắn Builder vào
    director = CVDirector(builder)
    
    # Director ra lệnh xây CV theo thứ tự
    html_result = director.construct(cv_data)
    
    return html_result, None
