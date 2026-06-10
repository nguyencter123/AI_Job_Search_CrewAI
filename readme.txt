clone về thì làm như sau để chạy

# Tạo môi trường ảo (ngang bằng với các thư mục dât, view...)
python -m venv venv

# Kích hoạt môi trường (Windows)
.\venv\Scripts\activate

Cài đặt các thư viện cần thiết:

pip install streamlit sqlalchemy mysql-connector-python bcrypt google-generativeai python-dotenv


Cài xampp
vào mysql tạo db CREATE DATABASE ai_job_search;

cấu hình file .env ( tự tạo file có nội dung như sau):

DB_URL="mysql+pymysql://root:@localhost:3306/ai_job_search"
GEMINI_API_KEY="API của mọi người"

sau đó chạy lệnh này để tạo các bảnggit
python create_db.py

ĐỂ chạy project thì chạy như sau: streamlit run app.py
Lưu ý là khi chạy thì cần khởi động môi trường ảo, trong hướng dẫn này ở phần đầu dã khởi động rồi
làm lần lượt thì đến đây ko cần khởi động nữa
Code kích hoạt mt ảo cho ai cần: .\venv\Scripts\activate
