import streamlit as st
import pandas as pd
from services.user_service import get_employer_info
from services.employer.job_service import get_employer_jobs, add_new_job, edit_job, remove_job

# --- CSS Tùy chỉnh để làm đẹp thẻ (Card) công việc ---
def load_custom_css():
    st.markdown("""
        <style>
        .job-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #f1f5f9;
            margin-bottom: 15px;
            transition: all 0.2s ease;
        }
        .job-card:hover {
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
            border-color: #e2e8f0;
        }
        .job-title {
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 5px;
        }
        .job-meta {
            font-size: 14px;
            color: #64748b;
            margin-bottom: 15px;
        }
        .status-badge.active {
            background-color: #dcfce7;
            color: #166534;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-badge.inactive {
            background-color: #fee2e2;
            color: #991b1b;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Các Popup Dialogs (Cửa sổ nổi) ---

@st.dialog("➕ Đăng tin tuyển dụng mới", width="large")
def show_add_job_dialog(uid, company_name):
    st.write("Vui lòng điền thông tin chi tiết về vị trí bạn muốn tuyển dụng.")
    with st.form(key="add_job_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Chức danh (*)", placeholder="Ví dụ: Senior Python Developer")
            location = st.text_input("Địa điểm", placeholder="Ví dụ: Hà Nội")
            salary = st.text_input("Mức lương", placeholder="Ví dụ: 20 - 30 Triệu")
        with col2:
            email = st.text_input("Email nhận CV (*)", placeholder="Ví dụ: hr@company.com")
            quantity = st.number_input("Số lượng tuyển", min_value=1, value=1)
            
        short_desc = st.text_area("Mô tả ngắn (Hiển thị ở trang chủ)", placeholder="Tóm tắt yêu cầu công việc trong 1-2 câu...")
        full_jd = st.text_area("Mô tả chi tiết (JD)", height=200, placeholder="Chi tiết công việc, yêu cầu, quyền lợi...")
        
        if st.form_submit_button("🚀 Đăng tin ngay", type="primary", use_container_width=True):
            if not title or not email:
                st.error("Vui lòng nhập Chức danh và Email nhận CV!")
            else:
                success, err = add_new_job(uid, company_name, title, location, salary, short_desc, full_jd, email, quantity)
                if success:
                    st.success("🎉 Đã đăng tin tuyển dụng thành công!")
                    st.rerun()
                else:
                    st.error(err)

@st.dialog("📝 Chỉnh sửa tin tuyển dụng", width="large")
def show_edit_job_dialog(job, uid):
    st.write(f"Đang chỉnh sửa: **{job['title']}**")
    with st.form(key=f"edit_form_{job['id']}"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Chức danh", value=job['title'])
            location = st.text_input("Địa điểm", value=job['location'])
            salary = st.text_input("Mức lương", value=job['salary'])
        with col2:
            email = st.text_input("Email nhận CV", value=job['contact_email'])
            quantity = st.number_input("Số lượng tuyển", min_value=1, value=job['quantity'])
            is_active = st.toggle("Trạng thái hiển thị", value=job['is_active'])
            
        short_desc = st.text_area("Mô tả ngắn", value=job['short_desc'])
        full_jd = st.text_area("Mô tả chi tiết (JD)", value=job['full_jd'], height=200)
        
        if st.form_submit_button("💾 Lưu thay đổi", type="primary", use_container_width=True):
            success, err = edit_job(job['id'], uid, title, location, salary, short_desc, full_jd, email, quantity, is_active)
            if success:
                st.success("Cập nhật thành công!")
                st.rerun()
            else:
                st.error(err)

@st.dialog("⚠️ Xác nhận xóa", width="small")
def show_delete_confirm_dialog(job, uid):
    st.error(f"Bạn có chắc chắn muốn xóa tin tuyển dụng **{job['title']}** không? Hành động này không thể hoàn tác.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Hủy bỏ", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🗑️ Xóa ngay", type="primary", use_container_width=True):
            success, err = remove_job(job['id'], uid)
            if success:
                st.rerun()
            else:
                st.error(err)

# --- Màn hình chính ---

def render_employer_dashboard():
    load_custom_css()
    uid = st.session_state["user_id"]
    employer_info = get_employer_info(uid)
    company_name = employer_info.get('company_name', 'Nhà Tuyển Dụng')
    
    # Header
    col_header, col_logout = st.columns([4, 1])
    with col_header:
        st.markdown(f"<h1 style='color: #0f172a; margin-bottom: 0;'>👋 Xin chào, {company_name}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 16px;'>Chào mừng bạn đến với Hệ thống Quản trị Tuyển dụng AI</p>", unsafe_allow_html=True)
    with col_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
    st.divider()
    
    tab1, tab2 = st.tabs(["📋 Tin tuyển dụng", "🏢 Hồ sơ công ty"])
    
    with tab1:
        # Toolbar
        col_count, col_add = st.columns([3, 1])
        with col_add:
            if st.button("➕ Thêm tin tuyển dụng", type="primary", use_container_width=True):
                show_add_job_dialog(uid, company_name)
                
        # Job List
        jobs = get_employer_jobs(uid)
        
        with col_count:
            active_count = sum(1 for j in jobs if j['is_active'])
            st.markdown(f"**Tổng số:** {len(jobs)} tin (Đang hiển thị: {active_count})")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if not jobs:
            st.info("Chưa có tin tuyển dụng nào. Hãy tạo tin đầu tiên của bạn!")
        else:
            import math
            PAGE_SIZE = 20
            total_pages = math.ceil(len(jobs) / PAGE_SIZE)
            
            if "emp_jobs_page" not in st.session_state:
                st.session_state["emp_jobs_page"] = 1
                
            if st.session_state["emp_jobs_page"] > total_pages:
                st.session_state["emp_jobs_page"] = 1
                
            current_page = st.session_state["emp_jobs_page"]
            start_idx = (current_page - 1) * PAGE_SIZE
            end_idx = start_idx + PAGE_SIZE
            
            paged_jobs = jobs[start_idx:end_idx]
            
            for job in paged_jobs:
                status_class = "active" if job['is_active'] else "inactive"
                status_text = "Đang hiển thị" if job['is_active'] else "Đã ẩn"
                
                # HTML Card
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div class="job-title">{job['title']}</div>
                            <div class="job-meta">
                                📍 {job['location']} &nbsp; | &nbsp; 💰 {job['salary']} &nbsp; | &nbsp; 👥 SL: {job['quantity']}
                            </div>
                        </div>
                        <span class="status-badge {status_class}">{status_text}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action Buttons (Streamlit buttons right below the card HTML)
                col_btn1, col_btn2, col_space = st.columns([1, 1, 6])
                with col_btn1:
                    if st.button("✏️ Chỉnh sửa", key=f"edit_{job['id']}", use_container_width=True):
                        show_edit_job_dialog(job, uid)
                with col_btn2:
                    if st.button("🗑️ Xóa", key=f"del_btn_{job['id']}", use_container_width=True):
                        show_delete_confirm_dialog(job, uid)
                st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
                
            # Điều hướng phân trang
            if total_pages > 1:
                st.markdown("<br>", unsafe_allow_html=True)
                col_prev, col_page, col_next = st.columns([1, 2, 1])
                with col_prev:
                    if st.button("⬅️ Trang trước", key="emp_prev", use_container_width=True, disabled=(current_page == 1)):
                        st.session_state["emp_jobs_page"] -= 1
                        st.rerun()
                with col_page:
                    st.markdown(f"<div style='text-align: center; padding-top: 5px;'><b>Trang {current_page} / {total_pages}</b></div>", unsafe_allow_html=True)
                with col_next:
                    if st.button("Trang sau ➡️", key="emp_next", use_container_width=True, disabled=(current_page == total_pages)):
                        st.session_state["emp_jobs_page"] += 1
                        st.rerun()

    with tab2:
        with st.container(border=True):
            col_info, col_img = st.columns([3, 1])
            with col_info:
                st.markdown("### Thông tin Doanh nghiệp")
                st.markdown(f"**Tên công ty:** {employer_info.get('company_name')}")
                st.markdown(f"**Website:** [{employer_info.get('website')}]({employer_info.get('website')})")
                st.markdown(f"**Địa chỉ trụ sở:** {employer_info.get('address')}")
                
                st.markdown("### Giới thiệu chung")
                st.markdown(f"<div style='background-color: #f8fafc; padding: 15px; border-radius: 8px;'>{employer_info.get('company_description')}</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✏️ Cập nhật thông tin công ty"):
                # Vì chưa có dialog cho update công ty, ta có thể dẫn họ lại trang setup
                # hoặc đơn giản là set lại state. Nhưng hiện tại họ có thể chỉnh sửa ở profile_setup
                st.info("Để chỉnh sửa, vui lòng liên hệ Admin. (Chức năng tự cập nhật sẽ sớm ra mắt!)")
