# File: migrate_db.py
from sqlalchemy import text
from repositories.database import engine, Base
from repositories import models

def migrate():
    print("--- Đang bắt đầu cập nhật cấu trúc Cơ sở dữ liệu ---")
    
    # 1. Tạo các bảng mới (EmployerProfile, Job)
    print("1. Tạo các bảng mới nếu chưa có...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Chạy lệnh SQL để ALTER các bảng cũ
    print("2. Cập nhật các cột trong các bảng cũ...")
    with engine.begin() as connection:
        try:
            # Sửa cột role trong bảng users để thêm 'job_poster'
            connection.execute(text("ALTER TABLE users MODIFY COLUMN role ENUM('user', 'admin', 'job_poster') DEFAULT 'user';"))
            print(" - Cập nhật cột role trong bảng users thành công.")
        except Exception as e:
            print(f" - Lỗi hoặc đã cập nhật cột role: {e}")

        try:
            # Xóa hết dữ liệu cũ trong bảng matches và documents để đổi kiểu dữ liệu an toàn
            connection.execute(text("TRUNCATE TABLE user_job_matches;"))
            connection.execute(text("TRUNCATE TABLE application_documents;"))
            
            # Đổi kiểu dữ liệu job_id từ VARCHAR(100) sang INT
            connection.execute(text("ALTER TABLE user_job_matches MODIFY COLUMN job_id INT NOT NULL;"))
            connection.execute(text("ALTER TABLE application_documents MODIFY COLUMN job_id INT NOT NULL;"))
            print(" - Cập nhật kiểu dữ liệu job_id thành công.")
        except Exception as e:
            print(f" - Lỗi hoặc đã cập nhật cột job_id: {e}")

    print("✅ Hoàn tất cập nhật CSDL!")

if __name__ == "__main__":
    migrate()
