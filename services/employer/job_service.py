# File: services/job_service.py
from repositories.database import db_session
from repositories.employer.job_repo import (
    create_job as _repo_create_job,
    update_job as _repo_update_job,
    delete_job as _repo_delete_job,
    get_jobs_by_poster as _repo_get_jobs_by_poster,
    get_job_by_id as _repo_get_job_by_id
)

def get_employer_jobs(poster_id: int) -> list:
    """Lấy danh sách công việc do nhà tuyển dụng này đăng tải."""
    with db_session() as db:
        jobs = _repo_get_jobs_by_poster(db, poster_id)
        # Chuyển đổi thành dict để UI dễ dùng
        return [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "salary": j.salary,
                "short_desc": j.short_desc,
                "full_jd": j.full_jd,
                "contact_email": j.contact_email,
                "quantity": j.quantity,
                "is_active": j.is_active,
                "created_at": j.created_at
            } for j in jobs
        ]

def add_new_job(poster_id: int, company: str, title: str, location: str, salary: str, short_desc: str, full_jd: str, contact_email: str, quantity: int) -> tuple[bool, str | None]:
    """Thêm tin tuyển dụng mới."""
    if not title or not company:
        return False, "Thiếu thông tin bắt buộc (Tiêu đề, Tên công ty)."
    
    with db_session() as db:
        new_job = _repo_create_job(db, poster_id, title, company, location, salary, short_desc, full_jd, contact_email, quantity)
        if new_job:
            return True, None
    return False, "Không thể tạo tin tuyển dụng lúc này."

def edit_job(job_id: int, poster_id: int, title: str, location: str, salary: str, short_desc: str, full_jd: str, contact_email: str, quantity: int, is_active: bool) -> tuple[bool, str | None]:
    """Cập nhật tin tuyển dụng."""
    if not title:
        return False, "Tiêu đề không được để trống."
        
    with db_session() as db:
        job = _repo_update_job(db, job_id, poster_id, title, location, salary, short_desc, full_jd, contact_email, quantity, is_active)
        if job:
            return True, None
    return False, "Tin tuyển dụng không tồn tại hoặc bạn không có quyền sửa."

def remove_job(job_id: int, poster_id: int) -> tuple[bool, str | None]:
    """Xóa tin tuyển dụng."""
    with db_session() as db:
        success = _repo_delete_job(db, job_id, poster_id)
        if success:
            return True, None
    return False, "Tin tuyển dụng không tồn tại hoặc bạn không có quyền xóa."
