# File: services/ai_service.py
import json
import os
import re
import time

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Model dự phòng khi model chính bị 429 (quota free tier tách theo model)
_FALLBACK_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
)


def _strip_code_fences(text: str) -> str:
    s = text.strip()
    if "```" in s:
        parts = re.split(r"```(?:json)?\s*", s, flags=re.IGNORECASE)
        if len(parts) >= 2:
            s = parts[1].split("```", 1)[0].strip()
        else:
            s = s.replace("```json", "").replace("```", "").strip()
    return s


def _fix_trailing_commas(fragment: str) -> str:
    return re.sub(r",(\s*[\]}])", r"\1", fragment)


def _parse_ranking_json(raw_text: str) -> list:
    s = _strip_code_fences(raw_text)
    start = s.find("[")
    if start == -1:
        raise ValueError("Phản hồi AI không chứa mảng JSON (không thấy ký tự '[').")

    decoder = json.JSONDecoder()
    tail = s[start:]
    try:
        data, _ = decoder.raw_decode(tail)
    except json.JSONDecodeError:
        data, _ = decoder.raw_decode(_fix_trailing_commas(tail))

    if not isinstance(data, list):
        raise ValueError("JSON phải là một mảng các object.")
    return data


def _is_quota_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return (
        "429" in str(exc)
        or "quota" in msg
        or "rate" in msg
        or "resource_exhausted" in msg
        or "depleted" in msg
        or "prepayment" in msg
    )


def _format_api_error(exc: Exception) -> str:
    msg = str(exc)
    lower = msg.lower()
    if "prepayment" in lower and "depleted" in lower:
        return (
            "Tài khoản Google AI đã hết credit (prepayment depleted). "
            "Tạo API key mới KHÔNG giúp nếu vẫn cùng project Google — cần: "
            "(1) đăng nhập Google khác → tạo key mới trên https://aistudio.google.com/apikey, hoặc "
            "(2) vào https://ai.studio/projects nạp/bật billing cho project hiện tại."
        )
    if _is_quota_error(exc):
        return (
            "Đã vượt hạn mức API Gemini. Tạo key mới trên tài khoản Google khác, "
            "đặt GEMINI_MAX_JOBS=5, lọc ít việc, hoặc bật billing tại https://ai.studio/projects"
        )
    lower = msg.lower()
    if "403" in msg or "leaked" in lower:
        return "API key bị Google từ chối. Tạo key mới tại https://aistudio.google.com/apikey"
    return f"Lỗi xử lý AI: {msg}"


def _model_candidates() -> list[str]:
    primary = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    seen = set()
    out = []
    for name in [primary, *_FALLBACK_MODELS]:
        if name and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def _build_generation_config():
    try:
        return genai.GenerationConfig(response_mime_type="application/json")
    except (AttributeError, TypeError, ValueError):
        return None


def _generate_ranking(model_name: str, prompt: str):
    model = genai.GenerativeModel(model_name)
    cfg = _build_generation_config()
    if cfg is not None:
        return model.generate_content(prompt, generation_config=cfg)
    return model.generate_content(prompt)


def _score_one_batch(skills: str, experience: str, batch: list, model_candidates: list):
    """Gọi AI chấm điểm cho 1 batch nhỏ. Trả về (ranked_data, error)."""
    simplified_jobs = [
        {
            "id": j["id"],
            "title": j["title"],
            "desc": (j.get("short_desc") or "")[:120],
        }
        for j in batch
    ]

    prompt = f"""
Bạn là hệ thống AI hỗ trợ tuyển dụng. Chấm điểm phù hợp 0-100 cho từng job.

[HỒ SƠ]
Kỹ năng: {skills}
Kinh nghiệm: {experience}

[JOBS]
{json.dumps(simplified_jobs, ensure_ascii=False)}

Trả về DUY NHẤT một mảng JSON, không markdown:
[{{"id":"JOB_xxx","score":85,"reason":"một câu ngắn tiếng Việt"}}]
Sắp xếp giảm dần theo score. id phải khớp danh sách. reason không chứa dấu ngoặc kép.
"""

    last_error = None
    for model_name in model_candidates:
        try:
            response = _generate_ranking(model_name, prompt)
            raw = (response.text or "").strip()
            if not raw:
                last_error = Exception("AI không trả về nội dung.")
                continue

            ranked_data = _parse_ranking_json(raw)
            return ranked_data, None
        except json.JSONDecodeError as e:
            return None, f"Lỗi parse JSON từ AI ({model_name}): {e}"
        except Exception as e:
            last_error = e
            if _is_quota_error(e):
                time.sleep(2)
                continue
            return None, _format_api_error(e)

    return None, _format_api_error(last_error or Exception("Không gọi được Gemini API."))


def analyze_and_rank_jobs(skills: str, experience: str, jobs_list: list):
    """
    Chấm điểm TẤT CẢ công việc bằng cách chia nhỏ thành từng batch.
    Mỗi batch gửi tối đa GEMINI_MAX_JOBS (mặc định 5) jobs cho AI.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "Điền_Key_Của_Bạn_Vào_Đây":
        return None, "Lỗi: Chưa cấu hình GEMINI_API_KEY trong file .env"

    genai.configure(api_key=api_key)

    batch_size = int(os.getenv("GEMINI_MAX_JOBS", "5"))
    model_candidates = _model_candidates()

    # Chia danh sách jobs thành các batch nhỏ
    batches = [
        jobs_list[i : i + batch_size]
        for i in range(0, len(jobs_list), batch_size)
    ]

    all_ranked = []
    for idx, batch in enumerate(batches):
        ranked_data, error = _score_one_batch(skills, experience, batch, model_candidates)

        if error:
            # Nếu batch nào bị lỗi, trả về kết quả đã chấm được + thông báo
            if all_ranked:
                return all_ranked, None  # Trả về những gì đã chấm được
            return None, error

        if ranked_data:
            all_ranked.extend(ranked_data)

        # Chờ 4 giây giữa các batch để tránh bị giới hạn tốc độ (rate limit)
        if idx < len(batches) - 1:
            time.sleep(4)

    if not all_ranked:
        return None, "AI không trả về dữ liệu xếp hạng."

    # Sắp xếp lại toàn bộ theo điểm từ cao → thấp
    all_ranked.sort(key=lambda x: x.get("score", 0), reverse=True)

    return all_ranked, None
