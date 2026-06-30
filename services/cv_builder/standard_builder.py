# File: services/cv_builder/standard_builder.py
"""
Concrete Builder: Xây dựng CV theo mẫu Standard (Chuẩn).

Mẫu này tạo ra CV có giao diện:
- Header: Ảnh 3x4 bên trái + Họ tên, Email, SĐT bên phải
- Các section: Mục tiêu Nghề nghiệp, Kỹ năng, Kinh nghiệm, Học vấn
- Mỗi tiêu đề section có nền xám đậm, chữ trắng (theo mẫu CV gốc)

Vai trò trong Builder Pattern:
- StandardCVBuilder = Concrete Builder (Thợ xây cụ thể)
- Nó biết cách xây CV theo PHONG CÁCH cụ thể này
"""
import re
from services.cv_builder.base import ICVBuilder


class StandardCVBuilder(ICVBuilder):
    """Concrete Builder: Xây CV theo mẫu Standard (tiêu đề nền xám, layout 1 cột).
    
    Product (Sản phẩm) được lưu trữ trong self._html_parts dưới dạng
    các đoạn HTML. Khi gọi get_result(), tất cả sẽ được ghép lại thành
    một trang HTML hoàn chỉnh.
    """

    def __init__(self):
        self._html_parts: list[str] = []
        self._css = self._build_css()

    def reset(self):
        """Xóa trắng CV, chuẩn bị xây mới."""
        self._html_parts = []

    # ─── CSS cho mẫu Standard ──────────────────────────
    @staticmethod
    def _build_css() -> str:
        return """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            padding: 20px;
        }
        
        .cv-page {
            width: 794px;  /* A4 width */
            min-height: 1123px;  /* A4 height */
            background: #ffffff;
            padding: 40px 45px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        /* ─── Header ─── */
        .cv-header {
            display: flex;
            align-items: flex-start;
            gap: 25px;
            margin-bottom: 28px;
            padding-bottom: 20px;
            border-bottom: 2px solid #333;
        }
        .avatar-box {
            width: 110px;
            height: 140px;
            border: 2px solid #999;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            background: #f5f5f5;
            overflow: hidden;
        }
        .avatar-box img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .avatar-placeholder {
            color: #999;
            font-size: 13px;
            text-align: center;
        }
        .header-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .header-info h1 {
            font-size: 26px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .contact-row {
            display: flex;
            flex-wrap: wrap;
            gap: 18px;
            font-size: 13px;
            color: #555;
        }
        .contact-row span {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        /* ─── Sections ─── */
        .section {
            margin-bottom: 22px;
        }
        .section-title {
            background: #4a4a4a;
            color: #ffffff;
            font-size: 14px;
            font-weight: 700;
            padding: 8px 15px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .section-content {
            padding: 0 5px;
            font-size: 13.5px;
            line-height: 1.75;
            color: #333;
        }
        .section-content p {
            margin-bottom: 8px;
        }
        
        /* ─── Skills list ─── */
        .skills-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4px 30px;
            padding: 0 5px;
        }
        .skill-item {
            font-size: 13.5px;
            color: #333;
            padding: 3px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .skill-bullet {
            width: 7px;
            height: 7px;
            background: #4a4a4a;
            border-radius: 50%;
            flex-shrink: 0;
        }
        
        /* ─── Experience ─── */
        .exp-item {
            margin-bottom: 14px;
            padding-left: 5px;
        }
        .exp-item:last-child { margin-bottom: 0; }
        .exp-header {
            font-weight: 600;
            font-size: 14px;
            color: #1a1a1a;
            margin-bottom: 4px;
        }
        .exp-detail {
            font-size: 13px;
            color: #555;
            line-height: 1.7;
        }
        
        /* ─── Print ─── */
        @media print {
            body { background: white; padding: 0; }
            .cv-page { box-shadow: none; width: 100%; }
        }
        """

    # ─── Bước 1: Xây Header ──────────────────────────
    def build_header(self, full_name: str, email: str = "", 
                     phone: str = "", avatar_base64: str = ""):
        """Xây phần đầu CV: Ảnh 3x4 + Tên + Liên hệ."""
        # Avatar
        if avatar_base64:
            avatar_html = f'<img src="data:image/jpeg;base64,{avatar_base64}" alt="Ảnh đại diện">'
        else:
            avatar_html = '<div class="avatar-placeholder">ẢNH<br>3x4</div>'

        # Contact info
        contact_parts = []
        if email:
            contact_parts.append(f'<span>📧 {email}</span>')
        if phone:
            contact_parts.append(f'<span>📱 {phone}</span>')

        contact_html = "".join(contact_parts)

        self._html_parts.append(f"""
        <div class="cv-header">
            <div class="avatar-box">{avatar_html}</div>
            <div class="header-info">
                <h1>{full_name}</h1>
                <div class="contact-row">{contact_html}</div>
            </div>
        </div>
        """)

    # ─── Bước 2: Xây Mục tiêu Nghề nghiệp ───────────
    def build_objective(self, objective_text: str):
        """Xây phần Mục tiêu Nghề nghiệp."""
        if not objective_text or not objective_text.strip():
            content = "<p><em>Đang cập nhật...</em></p>"
        else:
            paragraphs = objective_text.strip().split("\n")
            content = "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())
        
        self._html_parts.append(f"""
        <div class="section">
            <div class="section-title">MỤC TIÊU NGHỀ NGHIỆP</div>
            <div class="section-content">{content}</div>
        </div>
        """)

    # ─── Bước 3: Xây Kỹ năng ─────────────────────────
    def build_skills(self, skills_text: str):
        """Xây phần Kỹ năng dạng bullet points 2 cột."""
        if not skills_text or not skills_text.strip():
            items_html = '<div class="skill-item"><div class="skill-bullet"></div><span><em>Đang cập nhật...</em></span></div>'
        else:
            # Tách kỹ năng bằng XUỐNG DÒNG hoặc dấu chấm phẩy (KHÔNG tách bằng dấu phẩy)
            # Ví dụ: "biết sử dụng python, C#, C++" → giữ nguyên 1 dòng
            raw_skills = re.split(r'[\n;•]+', skills_text)
            skills = [s.strip() for s in raw_skills if s.strip()]
            
            if not skills:
                skills = ["Đang cập nhật..."]
            
            items_html = ""
            for skill in skills:
                items_html += f"""
                <div class="skill-item">
                    <div class="skill-bullet"></div>
                    <span>{skill}</span>
                </div>
                """
        
        self._html_parts.append(f"""
        <div class="section">
            <div class="section-title">KỸ NĂNG</div>
            <div class="skills-grid">{items_html}</div>
        </div>
        """)

    # ─── Bước 4: Xây Kinh nghiệm Làm việc ───────────
    def build_experience(self, experience_text: str):
        """Xây phần Kinh nghiệm Làm việc."""
        if not experience_text or not experience_text.strip():
            content_html = '<div class="exp-detail"><em>Đang cập nhật...</em></div>'
        else:
            lines = experience_text.strip().split("\n")
            content_html = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Dòng bắt đầu bằng ## hoặc ** là tiêu đề công việc
                if line.startswith("##") or line.startswith("**"):
                    clean = line.lstrip("#* ").rstrip("*")
                    content_html += f'<div class="exp-header">{clean}</div>'
                # Dòng bắt đầu bằng - hoặc • là chi tiết
                elif line.startswith("-") or line.startswith("•"):
                    clean = line.lstrip("-• ").strip()
                    content_html += f'<div class="exp-detail">• {clean}</div>'
                else:
                    content_html += f'<div class="exp-detail">{line}</div>'
        
        self._html_parts.append(f"""
        <div class="section">
            <div class="section-title">KINH NGHIỆM LÀM VIỆC</div>
            <div class="exp-item">{content_html}</div>
        </div>
        """)

    # ─── Bước 5: Xây Học vấn ─────────────────────────
    def build_education(self, education_text: str):
        """Xây phần Học vấn."""
        if not education_text or not education_text.strip():
            content_html = '<div class="exp-detail"><em>Đang cập nhật...</em></div>'
        else:
            lines = education_text.strip().split("\n")
            content_html = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("##") or line.startswith("**"):
                    clean = line.lstrip("#* ").rstrip("*")
                    content_html += f'<div class="exp-header">{clean}</div>'
                elif line.startswith("-") or line.startswith("•"):
                    clean = line.lstrip("-• ").strip()
                    content_html += f'<div class="exp-detail">• {clean}</div>'
                else:
                    content_html += f'<div class="exp-detail">{line}</div>'
        
        self._html_parts.append(f"""
        <div class="section">
            <div class="section-title">HỌC VẤN</div>
            <div class="exp-item">{content_html}</div>
        </div>
        """)

    # ─── Lấy sản phẩm cuối cùng (Product) ────────────
    def get_result(self) -> str:
        """Trả về Product: Trang HTML hoàn chỉnh chứa CV."""
        body = "\n".join(self._html_parts)
        return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV - Curriculum Vitae</title>
    <style>{self._css}</style>
</head>
<body>
    <div class="cv-page">
        {body}
    </div>
</body>
</html>"""
