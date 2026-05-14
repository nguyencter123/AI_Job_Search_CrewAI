import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# 1. Lấy đường dẫn kết nối DB
DATABASE_URL = os.getenv("DB_URL")

# 2. Tạo Engine (Động cơ kết nối)
engine = create_engine(DATABASE_URL, echo=True)

# 3. Tạo SessionLocal (Phiên làm việc với CSDL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Tạo Base (Khuôn mẫu gốc cho các bảng sau này kế thừa)
Base = declarative_base()

# 5. Hàm cung cấp session (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()