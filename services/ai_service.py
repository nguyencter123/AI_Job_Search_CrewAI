# File: services/ai_service.py
import os
import json
import google.generativeai as genai

def analyze_and_rank_jobs(skills: str, experience: str, jobs_list: list):
    """
    Gọi Gemini AI để đánh giá độ phù hợp của ứng viên với danh sách công việc.
    """
    # Lấy key từ biến môi trường
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "Điền_Key_Của_Bạn_Vào_Đây":
        return None, "Lỗi: Chưa cấu hình GEMINI_API_KEY trong file .env"

    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Thu gọn dữ liệu gửi đi để tiết kiệm token và tăng tốc độ AI
    simplified_jobs = [{"id": j["id"], "title": j["title"], "desc": j["short_desc"]} for j in jobs_list]
    
    prompt = f"""
    Bạn là một hệ thống Trí tuệ Nhân tạo hỗ trợ tuyển dụng.
    Hãy đánh giá mức độ phù hợp (từ 0 đến 100) của ứng viên sau đối với danh sách công việc bên dưới.
    
    [HỒ SƠ ỨNG VIÊN]
    - Kỹ năng: {skills}
    - Kinh nghiệm: {experience}
    
    [DANH SÁCH CÔNG VIỆC]
    {json.dumps(simplified_jobs, ensure_ascii=False)}
    
    [YÊU CẦU ĐẦU RA]
    1. Trả về định dạng JSON Array chứa kết quả đánh giá cho TẤT CẢ công việc.
    2. Sắp xếp giảm dần theo điểm số (score).
    3. Trả về đúng định dạng này, không kèm bất kỳ văn bản nào khác, không dùng markdown code block:
    [
        {{"id": "Mã công việc", "score": Điểm số, "reason": "1 câu ngắn gọn (< 15 từ) giải thích lý do"}}
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        # Làm sạch chuỗi trả về đề phòng AI tự chèn markdown ```json
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        ranked_data = json.loads(raw_text)
        return ranked_data, None
    except Exception as e:
        return None, f"Lỗi xử lý AI: {str(e)}"