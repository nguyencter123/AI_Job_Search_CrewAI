# File: migrate_auth.py
"""
Script cập nhật CSDL để hỗ trợ đăng nhập đa phương thức (Factory Pattern).
Thêm các cột: phone_number, facebook_id, auth_provider
Sửa cột: email và password_hash thành nullable
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)

MIGRATIONS = [
    # 1. Thêm cột phone_number
    """
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20) UNIQUE DEFAULT NULL
    AFTER email;
    """,
    # 2. Thêm cột facebook_id
    """
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS facebook_id VARCHAR(100) UNIQUE DEFAULT NULL
    AFTER phone_number;
    """,
    # 3. Thêm cột auth_provider
    """
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS auth_provider ENUM('email', 'phone', 'facebook') DEFAULT 'email'
    AFTER password_hash;
    """,
    # 4. Cho phép email có thể NULL (vì đăng nhập bằng SĐT hoặc Facebook không cần email)
    """
    ALTER TABLE users
    MODIFY COLUMN email VARCHAR(255) DEFAULT NULL;
    """,
    # 5. Cho phép password_hash có thể NULL (vì Facebook không cần mật khẩu)
    """
    ALTER TABLE users
    MODIFY COLUMN password_hash VARCHAR(255) DEFAULT NULL;
    """,
]

def run():
    print("🔧 Bắt đầu cập nhật CSDL cho Factory Pattern Auth...")
    with engine.connect() as conn:
        for i, sql in enumerate(MIGRATIONS, 1):
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"  ✅ Bước {i}/{len(MIGRATIONS)}: Thành công!")
            except Exception as e:
                # Bỏ qua lỗi "Duplicate column name" (cột đã tồn tại)
                if "Duplicate column name" in str(e):
                    print(f"  ⏭️  Bước {i}/{len(MIGRATIONS)}: Cột đã tồn tại, bỏ qua.")
                else:
                    print(f"  ❌ Bước {i}/{len(MIGRATIONS)}: Lỗi - {e}")
    print("\n✅ Hoàn tất cập nhật CSDL cho hệ thống đăng nhập đa phương thức!")

if __name__ == "__main__":
    run()
