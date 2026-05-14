# File: repositories/job_provider.py
import json
import os

def get_all_jobs():
    """Đọc danh sách công việc từ file JSON giả lập"""
    # Lấy đường dẫn tuyệt đối đến file vietnam_jobs.json
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'vietnam_jobs.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
            return jobs
    except FileNotFoundError:
        return [] # Nếu lỗi, trả về mảng rỗng để web không bị sập