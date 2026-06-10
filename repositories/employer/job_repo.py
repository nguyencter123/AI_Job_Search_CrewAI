# File: repositories/job_repo.py
from sqlalchemy.orm import Session
from repositories.models import Job

def get_jobs_by_poster(db: Session, poster_id: int):
    """Lấy danh sách công việc do một nhà tuyển dụng đăng tải."""
    return db.query(Job).filter(Job.poster_id == poster_id).all()

def get_job_by_id(db: Session, job_id: int):
    """Lấy thông tin chi tiết một công việc."""
    return db.query(Job).filter(Job.id == job_id).first()

def create_job(db: Session, poster_id: int, title: str, company: str, location: str, salary: str, short_desc: str, full_jd: str, contact_email: str, quantity: int = 1):
    """Tạo mới một tin tuyển dụng."""
    new_job = Job(
        poster_id=poster_id,
        title=title,
        company=company,
        location=location,
        salary=salary,
        short_desc=short_desc,
        full_jd=full_jd,
        contact_email=contact_email,
        quantity=quantity,
        is_active=True
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

def update_job(db: Session, job_id: int, poster_id: int, title: str, location: str, salary: str, short_desc: str, full_jd: str, contact_email: str, quantity: int, is_active: bool):
    """Cập nhật thông tin tuyển dụng (Chỉ người đăng mới được sửa)."""
    job = db.query(Job).filter(Job.id == job_id, Job.poster_id == poster_id).first()
    if job:
        job.title = title
        job.location = location
        job.salary = salary
        job.short_desc = short_desc
        job.full_jd = full_jd
        job.contact_email = contact_email
        job.quantity = quantity
        job.is_active = is_active
        db.commit()
        return job
    return None

def delete_job(db: Session, job_id: int, poster_id: int):
    """Xóa tin tuyển dụng (Chỉ người đăng mới được xóa)."""
    job = db.query(Job).filter(Job.id == job_id, Job.poster_id == poster_id).first()
    if job:
        db.delete(job)
        db.commit()
        return True
    return False

def get_active_jobs(db: Session):
    """Lấy danh sách tất cả các công việc đang hoạt động để hiển thị cho người tìm việc."""
    return db.query(Job).filter(Job.is_active == True).all()
