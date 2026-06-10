# File: import_mock_jobs.py
import json
import os
from repositories.database import db_session
from repositories.employer.job_repo import create_job
from repositories.user_repo import create_user
from services.auth_service import hash_password

def import_jobs():
    print("--- Bắt đầu Import Dữ liệu Công việc ---")
    
    # 1. Tạo một tài khoản Nhà tuyển dụng "mẫu" để gán các công việc này
    print("1. Đang tạo tài khoản nhà tuyển dụng mẫu...")
    employer_email = "admin_hr@jobhub.com"
    employer_pass = "123456"
    employer_name = "Hệ thống Job Hub"
    
    with db_session() as db:
        from repositories.models import User
        # Check if exists
        employer = db.query(User).filter(User.email == employer_email).first()
        if not employer:
            employer = create_user(db, employer_email, employer_pass, employer_name, role='job_poster')
            print(f" - Đã tạo tài khoản: {employer_email} (Mật khẩu: {employer_pass})")
        else:
            print(f" - Tài khoản {employer_email} đã tồn tại, sẽ sử dụng tài khoản này.")
            
        employer_id = employer.id
        
    # 2. Đọc file JSON và chèn vào DB
    print("2. Đang đọc dữ liệu từ vietnam_jobs.json...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', 'vietnam_jobs.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
            
        print(f" - Tìm thấy {len(jobs)} công việc. Bắt đầu chèn vào DB...")
        count = 0
        with db_session() as db:
            for job_data in jobs:
                # Gọi hàm create_job
                create_job(
                    db=db,
                    poster_id=employer_id,
                    title=job_data.get('title', ''),
                    company=job_data.get('company', ''),
                    location=job_data.get('location', ''),
                    salary=job_data.get('salary', ''),
                    short_desc=job_data.get('short_desc', ''),
                    full_jd=job_data.get('full_jd', ''),
                    contact_email=job_data.get('contact_email', 'hr@example.com'),
                    quantity=1 # Dữ liệu cũ không có số lượng, mặc định là 1
                )
                count += 1
                
        print(f"✅ Đã Import thành công {count} công việc vào Database!")
        print("Bây giờ bạn có thể đăng nhập bằng tài khoản:")
        print(f" - Email: {employer_email}")
        print(f" - Pass: {employer_pass}")
        print("Để quản lý toàn bộ 50 công việc này!")
        
    except FileNotFoundError:
        print("❌ Không tìm thấy file vietnam_jobs.json!")
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    import_jobs()
