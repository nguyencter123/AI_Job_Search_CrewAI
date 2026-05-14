# File: create_db.py
from repositories.database import engine, Base
from repositories import models  # Bắt buộc phải import models để SQLAlchemy nhận diện các bảng

def init_db():
    print("--- Đang bắt đầu khởi tạo các bảng trong Cơ sở dữ liệu ---")
    try:
        # Lệnh này sẽ tìm tất cả các class kế thừa từ Base và tạo bảng nếu chúng chưa tồn tại
        Base.metadata.create_all(bind=engine)
        print("✅ Chúc mừng! 5 bảng đã được tạo thành công trong MySQL.")
    except Exception as e:
        print(f"❌ Có lỗi xảy ra khi tạo bảng: {e}")

if __name__ == "__main__":
    init_db()