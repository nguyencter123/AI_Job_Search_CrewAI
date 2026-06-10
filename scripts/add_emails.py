import json
import re

file_path = 'd:/KTPM/CrewAi/data/vietnam_jobs.json'

with open(file_path, 'r', encoding='utf-8') as f:
    jobs = json.load(f)

for job in jobs:
    # Lấy tên công ty
    company = job.get('company', 'company')
    
    # Tạo domain email giả lập dựa trên tên công ty
    # VD: "FinTech Global VN" -> "fintechglobal"
    clean_company = company.lower()
    has_vn = 'vn' in clean_company
    
    clean_company = clean_company.replace(' vn', '')
    domain_base = re.sub(r'[^a-z0-9]', '', clean_company)
    
    # Nếu có chữ VN thì dùng đuôi .vn, ngược lại dùng đuôi .com
    domain_ext = ".vn" if has_vn else ".com"
    domain = f"{domain_base}{domain_ext}"
    
    # Thêm trường contact_email
    job['contact_email'] = f"tuyendung@{domain}"

# Ghi lại vào file
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(jobs, f, ensure_ascii=False, indent=4)

print(f"Đã cập nhật thành công {len(jobs)} công việc!")
