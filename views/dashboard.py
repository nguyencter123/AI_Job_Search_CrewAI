# File: views/dashboard.py
import streamlit as st
from repositories.database import SessionLocal
from repositories.models import User, UserProfile
from repositories.user_repo import update_user_profile
from views.utils import load_css
from repositories.job_provider import get_all_jobs
import time
from services.ai_service import analyze_and_rank_jobs
def get_user_info(user_id):
    """Lấy thông tin người dùng từ DB để hiển thị lên giao diện"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        return user, profile
    finally:
        db.close()


import time
import streamlit as st
from services.ai_service import analyze_and_rank_jobs
from repositories.job_provider import get_all_jobs

def render_job_list():
    all_jobs = get_all_jobs()
    if not all_jobs:
        st.warning("Đang bảo trì hệ thống dữ liệu công việc. Vui lòng quay lại sau.")
        return

    user_id = st.session_state['user_id']
    from views.dashboard import get_user_info 
    user, profile = get_user_info(user_id)

    col_title, col_ai, col_filter = st.columns([4, 2, 2], vertical_alignment="bottom")
    
    with col_filter:
        with st.popover("⚙️ Bộ lọc", use_container_width=True):
            st.markdown("**Điều kiện tìm kiếm**")
            search_kw = st.text_input("🔑 Từ khóa", placeholder="VD: Python, React...")
            search_loc = st.selectbox("📍 Địa điểm", ["Tất cả", "Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Remote"])
            search_salary = st.radio("💰 Tiền tệ", ["Tất cả", "VNĐ", "USD"], horizontal=True)

    filtered_jobs = []
    for job in all_jobs:
        match_kw = True
        match_loc = True
        match_salary = True

        if search_kw:
            kw = search_kw.lower()
            search_area = f"{job['title']} {job['company']} {job['short_desc']}".lower()
            if kw not in search_area:
                match_kw = False

        if search_loc != "Tất cả" and search_loc.lower() not in job['location'].lower():
            match_loc = False
                
        if search_salary != "Tất cả" and search_salary.lower() not in job['salary'].lower():
            match_salary = False

        if match_kw and match_loc and match_salary:
            filtered_jobs.append(job)

    with col_title:
        st.markdown("### 🔍 Vị trí đề xuất cho bạn")
        st.caption(f"Đang hiển thị {len(filtered_jobs)}/{len(all_jobs)} công việc")

    # BƯỚC 1: Chỉ bắt sự kiện click nút (Không xử lý AI ở đây)
    with col_ai:
        analyze_btn = st.button("✨ Phân tích bằng AI", type="primary", use_container_width=True)

    st.divider()

    # BƯỚC 2: Tạo một vùng chứa (Placeholder) nằm ngay giữa màn hình
    loading_placeholder = st.empty()

    # BƯỚC 3: Đẩy giao diện xử lý AI vào vùng chứa rộng rãi kia
    if analyze_btn:
        if not profile or not profile.skills:
            st.error("⚠️ Hãy cập nhật Hồ sơ (Kỹ năng, Kinh nghiệm) trước!")
        elif not filtered_jobs:
            st.warning("⚠️ Không có công việc nào để phân tích!")
        else:
            with loading_placeholder.container():
                # Dùng CSS làm mờ nhẹ giao diện bên dưới để tập trung vào Spinner
                st.markdown("""
                    <style>
                    div[data-testid="stVerticalBlock"] > div:nth-child(n+6) {
                        opacity: 0.4;
                        pointer-events: none;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                with st.spinner("🧠 AI đang đọc hồ sơ và chấm điểm hàng loạt công việc... Vui lòng không thao tác gì thêm!"):
                    ranked_data, error = analyze_and_rank_jobs(profile.skills, profile.experience_summary, filtered_jobs)
                    
                    if error:
                        st.error(error)
                    else:
                        job_dict = {job['id']: job for job in filtered_jobs}
                        ai_sorted_jobs = []
                        for item in ranked_data:
                            job_info = job_dict.get(item['id'])
                            if job_info:
                                job_info['ai_score'] = item['score']
                                job_info['ai_reason'] = item['reason']
                                ai_sorted_jobs.append(job_info)
                        
                        st.session_state['ai_sorted_jobs'] = ai_sorted_jobs
                        st.success("🎉 Phân tích hoàn tất! Đang sắp xếp lại danh sách...")
                        time.sleep(1)
                        st.rerun()

    # 4. Hiển thị kết quả
    display_jobs = st.session_state.get('ai_sorted_jobs', filtered_jobs)

    if not display_jobs:
        st.info("🥲 Không tìm thấy công việc nào phù hợp với bộ lọc của bạn.")
    else:
        for job in display_jobs:
            is_ai_analyzed = 'ai_score' in job
            
            with st.container(border=True):
                col_info, col_btn = st.columns([4, 1])
                with col_info:
                    if is_ai_analyzed:
                        score_color = "#16a34a" if job['ai_score'] >= 80 else "#ca8a04" if job['ai_score'] >= 50 else "#dc2626"
                        st.markdown(f"#### {job['title']} <span style='font-size: 14px; color: white; background-color: {score_color}; padding: 3px 8px; border-radius: 12px; margin-left: 10px;'>🎯 Phù hợp: {job['ai_score']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"💡 **AI Nhận xét:** *{job['ai_reason']}*")
                    else:
                        st.markdown(f"#### {job['title']}")
                    
                    st.markdown(f"🏢 **{job['company']}** | 📍 {job['location']} | 💰 <span style='color: #16a34a; font-weight: bold;'>{job['salary']}</span>", unsafe_allow_html=True)
                    st.text(job['short_desc'])
                    
                    with st.expander("Xem chi tiết JD"):
                        st.text(job['full_jd'])
                        
                with col_btn:
                    st.write("") 
                    if st.button("🤖 Ứng tuyển AI", key=f"btn_{job['id']}", use_container_width=True):
                        st.session_state['selected_job'] = job
                        st.info(f"Đã chọn: {job['title']}. Hãy sang tab AI để bắt đầu!")


def render_dashboard():
    # 1. Load giao diện chuẩn
    load_css("assets/style.css")
    
    # 2. Lấy thông tin user
    user_id = st.session_state['user_id']
    user, profile = get_user_info(user_id)
    display_name = profile.full_name if profile and profile.full_name else user.email

    # --- THANH ĐIỀU HƯỚNG (SIDEBAR) ---
    with st.sidebar:
        st.markdown(f"<h2 style='text-align: center;'>💼 AI Job Hub</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>Xin chào, <b>{display_name}</b></p>", unsafe_allow_html=True)
        st.divider()
        
        menu_selection = st.radio(
            "📍 Điều hướng",
            ["🏠 Trang chủ", "👤 Hồ sơ cá nhân", "🤖 AI Tìm việc & Soạn CV", "📁 Lịch sử tài liệu"],
            label_visibility="collapsed"
        )
        
        st.spacer = st.container() # Tạo khoảng trống đẩy nút logout xuống dưới
        st.divider()
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state['user_id'] = None
            st.rerun()

    # --- KHU VỰC HIỂN THỊ CHÍNH ---
    if menu_selection == "🏠 Trang chủ":
        st.title("📊 Bảng điều khiển")
        render_job_list()
        
    elif menu_selection == "👤 Hồ sơ cá nhân":
        st.title("👤 Chỉnh sửa Hồ sơ Năng lực")
        st.write("Thông tin này sẽ là 'nguyên liệu' để AI viết CV cho bạn.")
        
        with st.form("update_profile_form"):
            new_skills = st.text_area("Kỹ năng hiện tại", value=profile.skills if profile.skills else "")
            new_exp = st.text_area("Kinh nghiệm làm việc", value=profile.experience_summary if profile.experience_summary else "", height=200)
            
            if st.form_submit_button("Cập nhật thay đổi"):
                db = SessionLocal()
                try:
                    update_user_profile(db, user_id, new_skills, new_exp)
                    st.success("Đã cập nhật hồ sơ thành công!")
                finally:
                    db.close()
        
    elif menu_selection == "🤖 AI Tìm việc & Soạn CV":
        st.title("🤖 Trợ lý AI (CrewAI)")
        
        # Kiểm tra xem người dùng đã chọn việc từ Trang chủ chưa
        job_context = st.session_state.get('selected_job', None)
        
        if job_context:
            st.success(f"Đang chuẩn bị hồ sơ cho vị trí: **{job_context['title']}** tại **{job_context['company']}**")
        
        jd_input = st.text_area("Dán Mô tả công việc (JD) vào đây:", 
                               value=job_context['desc'] if job_context else "",
                               height=250)
        
        if st.button("Kích hoạt Biệt đội AI 🚀", type="primary"):
            st.warning("Đang kết nối với CrewAI... (Phần này chúng ta sẽ code ở bước tiếp theo)")
        
    elif menu_selection == "📁 Lịch sử tài liệu":
        st.title("📁 Kho lưu trữ cá nhân")
        st.info("Danh sách CV và Cover Letter bạn đã tạo sẽ xuất hiện ở đây.")