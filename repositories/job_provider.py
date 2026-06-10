# File: repositories/job_provider.py
from repositories.database import db_session
from repositories.employer.job_repo import get_active_jobs

def get_all_jobs():
    """Lấy danh sách các công việc ĐANG HOẠT ĐỘNG từ Database."""
    with db_session() as db:
        jobs_orm = get_active_jobs(db)
        # Chuyển đổi sang list of dicts để tương thích ngược với code cũ
        return [
            {
                "id": str(j.id), # Ép kiểu sang chuỗi để tránh lỗi với code cũ nếu có
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "salary": j.salary,
                "short_desc": j.short_desc,
                "full_jd": j.full_jd,
                "contact_email": j.contact_email,
                "quantity": j.quantity
            } for j in jobs_orm
        ]