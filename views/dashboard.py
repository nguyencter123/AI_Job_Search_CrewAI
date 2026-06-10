# File: views/dashboard.py
import time

import streamlit as st

from services.user_service import get_user_info, update_profile
from services.job_matching_service import get_all_jobs
from services.matching.basic_matching import BasicMatchingStrategy
from services.matching.ai_matching import AiMatchingStrategy
from services.matching.engine import JobSearchEngine
from views.utils import load_css


def render_job_list():
    """Danh sách việc làm; user_id lấy từ session."""
    user_id = st.session_state["user_id"]
    all_jobs = get_all_jobs()
    if not all_jobs:
        st.warning("Đang bảo trì hệ thống dữ liệu công việc. Vui lòng quay lại sau.")
        return

    col_title, col_mode, col_filter = st.columns([4, 2, 2], vertical_alignment="bottom")

    with col_filter:
        with st.popover("⚙️ Bộ lọc", use_container_width=True):
            st.markdown("**Điều kiện tìm kiếm**")
            search_kw = st.text_input("🔑 Từ khóa", placeholder="VD: Python, React...")
            search_loc = st.text_input("📍 Địa điểm", placeholder="Nhập tỉnh/thành phố hoặc 'Remote'...")
            search_salary = st.radio("💰 Tiền tệ", ["Tất cả", "VNĐ", "USD"], horizontal=True)

    # === STRATEGY PATTERN: Cho người dùng chọn thuật toán ===
    with col_mode:
        search_mode = st.radio(
            "Chế độ tìm kiếm",
            ["🔍 Tìm nhanh", "🤖 AI phân tích"],
            horizontal=True,
            label_visibility="collapsed",
        )

    with col_title:
        st.markdown("### 🔍 Vị trí đề xuất cho bạn")

    st.divider()

    # === TẠO CONTEXT VÀ GẮN STRATEGY TÙY THEO LỰA CHỌN CỦA NGƯỜI DÙNG ===
    if "AI" in search_mode:
        # Người dùng chọn AI → Gắn AiMatchingStrategy vào Engine
        engine = JobSearchEngine(AiMatchingStrategy())
    else:
        # Người dùng chọn Tìm nhanh → Gắn BasicMatchingStrategy vào Engine
        engine = JobSearchEngine(BasicMatchingStrategy())

    # === CHẾ ĐỘ TÌM NHANH: Tự động chạy ngay ===
    if "Tìm nhanh" in search_mode:
        display_jobs, _ = engine.search(user_id, all_jobs, search_kw, search_loc, search_salary)
        st.caption(f"Đang hiển thị {len(display_jobs)}/{len(all_jobs)} công việc")
        # Xóa kết quả AI cũ nếu có
        st.session_state.pop("ai_sorted_jobs", None)

    # === CHẾ ĐỘ AI: Cần bấm nút để chạy ===
    else:
        analyze_btn = st.button("✨ Bắt đầu phân tích bằng AI", type="primary", use_container_width=True)
        loading_placeholder = st.empty()

        if analyze_btn:
            with loading_placeholder.container():
                with st.spinner(
                    "🧠 AI đang đọc hồ sơ và chấm điểm hàng loạt công việc... Vui lòng không thao tác gì thêm!"
                ):
                    # Engine ủy thác cho AiMatchingStrategy
                    ai_results, error = engine.search(user_id, all_jobs, search_kw, search_loc, search_salary)

                    if error:
                        st.error(error)
                    else:
                        st.session_state["ai_sorted_jobs"] = ai_results
                        st.success("🎉 Phân tích hoàn tất! Đang sắp xếp lại danh sách...")
                        time.sleep(1)
                        st.rerun()

        display_jobs = st.session_state.get("ai_sorted_jobs", None)
        if display_jobs is None:
            # Chưa chạy AI → hiện danh sách lọc cơ bản tạm thời
            basic_engine = JobSearchEngine(BasicMatchingStrategy())
            display_jobs, _ = basic_engine.search(user_id, all_jobs, search_kw, search_loc, search_salary)
        
        st.caption(f"Đang hiển thị {len(display_jobs)}/{len(all_jobs)} công việc")

    if not display_jobs:
        st.info("🥲 Không tìm thấy công việc nào phù hợp với bộ lọc của bạn.")
    else:
        import math
        PAGE_SIZE = 20
        total_pages = math.ceil(len(display_jobs) / PAGE_SIZE)
        
        if "user_jobs_page" not in st.session_state:
            st.session_state["user_jobs_page"] = 1
            
        # Đảm bảo page hiện tại không vượt quá tổng số page (do thay đổi filter)
        if st.session_state["user_jobs_page"] > total_pages:
            st.session_state["user_jobs_page"] = 1
            
        current_page = st.session_state["user_jobs_page"]
        start_idx = (current_page - 1) * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        
        paged_jobs = display_jobs[start_idx:end_idx]
        
        for job in paged_jobs:
            is_ai_analyzed = "ai_score" in job

            with st.container(border=True):
                col_info, col_btn = st.columns([4, 1])
                with col_info:
                    if is_ai_analyzed:
                        score_color = (
                            "#16a34a"
                            if job["ai_score"] >= 80
                            else "#ca8a04"
                            if job["ai_score"] >= 50
                            else "#dc2626"
                        )
                        st.markdown(
                            f"#### {job['title']} <span style='font-size: 14px; color: white; background-color: {score_color}; padding: 3px 8px; border-radius: 12px; margin-left: 10px;'>🎯 Phù hợp: {job['ai_score']}%</span>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"💡 **AI Nhận xét:** *{job['ai_reason']}*")
                    else:
                        st.markdown(f"#### {job['title']}")

                    st.markdown(
                        f"🏢 **{job['company']}** | 📍 {job['location']} | 💰 <span style='color: #16a34a; font-weight: bold;'>{job['salary']}</span>",
                        unsafe_allow_html=True,
                    )
                    if job.get("contact_email"):
                        st.markdown(f"📧 **Email liên hệ:** `{job['contact_email']}`")
                    st.text(job["short_desc"])

                    with st.expander("Xem chi tiết JD"):
                        st.text(job["full_jd"])

                with col_btn:
                    st.write("")
                    if st.button("🤖 Ứng tuyển AI", key=f"btn_{job['id']}", use_container_width=True):
                        st.session_state["selected_job"] = job
                        st.info(f"Đã chọn: {job['title']}. Hãy sang tab AI để bắt đầu!")
                        
        # Điều hướng phân trang
        st.markdown("<br>", unsafe_allow_html=True)
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("⬅️ Trang trước", use_container_width=True, disabled=(current_page == 1)):
                st.session_state["user_jobs_page"] -= 1
                st.rerun()
        with col_page:
            st.markdown(f"<div style='text-align: center; padding-top: 5px;'><b>Trang {current_page} / {total_pages}</b></div>", unsafe_allow_html=True)
        with col_next:
            if st.button("Trang sau ➡️", use_container_width=True, disabled=(current_page == total_pages)):
                st.session_state["user_jobs_page"] += 1
                st.rerun()


def render_dashboard():
    load_css("assets/style.css")

    user_id = st.session_state["user_id"]
    user_info = get_user_info(user_id)

    if not user_info:
        st.error("Không tìm thấy tài khoản. Vui lòng đăng nhập lại.")
        st.session_state["user_id"] = None
        st.session_state["role"] = None
        st.rerun()
        return

    display_name = user_info["display_name"]

    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>💼 AI Job Hub</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>Xin chào, <b>{display_name}</b></p>", unsafe_allow_html=True)
        st.divider()

        menu_selection = st.radio(
            "📍 Điều hướng",
            ["🏠 Trang chủ", "👤 Hồ sơ cá nhân", "🤖 AI Tìm việc & Soạn CV", "📁 Lịch sử tài liệu"],
            label_visibility="collapsed",
        )

        st.spacer = st.container()
        st.divider()
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    if menu_selection == "🏠 Trang chủ":
        st.title("📊 Bảng điều khiển")
        render_job_list()

    elif menu_selection == "👤 Hồ sơ cá nhân":
        st.title("👤 Chỉnh sửa Hồ sơ Năng lực")
        st.write("Thông tin này sẽ là 'nguyên liệu' để AI viết CV cho bạn.")

        # --- ẢNH ĐẠI DIỆN ---
        from services.user_service import upload_avatar, get_avatar

        st.markdown("#### 📷 Ảnh đại diện")
        avatar_data, avatar_mime = get_avatar(user_id)
        col_avatar, col_upload = st.columns([1, 2])
        with col_avatar:
            if avatar_data:
                st.image(avatar_data, caption="Ảnh hiện tại", width=150)
            else:
                st.info("Chưa có ảnh đại diện.")
        with col_upload:
            new_avatar = st.file_uploader(
                "Đổi ảnh đại diện",
                type=["jpg", "jpeg", "png"],
                help="Chỉ chấp nhận .jpg hoặc .png, tối đa 2MB.",
            )
            if new_avatar:
                st.image(new_avatar, caption="Ảnh mới (xem trước)", width=150)
                if st.button("📷 Lưu ảnh mới"):
                    ok, err = upload_avatar(user_id, new_avatar.getvalue(), new_avatar.type)
                    if ok:
                        st.success("Đã cập nhật ảnh đại diện!")
                        st.rerun()
                    else:
                        st.error(err)

        st.divider()

        # --- KỸ NĂNG & KINH NGHIỆM ---
        with st.form("update_profile_form"):
            new_skills = st.text_area(
                "Kỹ năng hiện tại",
                value=user_info["skills"],
            )
            new_exp = st.text_area(
                "Kinh nghiệm làm việc",
                value=user_info["experience_summary"],
                height=200,
            )

            if st.form_submit_button("Cập nhật thay đổi"):
                success, error = update_profile(user_id, new_skills, new_exp)
                if success:
                    st.success("Đã cập nhật hồ sơ thành công!")
                else:
                    st.error(error)

    elif menu_selection == "🤖 AI Tìm việc & Soạn CV":
        st.title("🤖 Trợ lý AI (CrewAI)")

        job_context = st.session_state.get("selected_job", None)

        if job_context:
            st.success(
                f"Đang chuẩn bị hồ sơ cho vị trí: **{job_context['title']}** tại **{job_context['company']}**"
            )

        jd_default = ""
        if job_context:
            jd_default = job_context.get("full_jd") or job_context.get("short_desc") or ""

        jd_input = st.text_area("Dán Mô tả công việc (JD) vào đây:", value=jd_default, height=250)

        if st.button("Kích hoạt Biệt đội AI 🚀", type="primary"):
            st.warning("Đang kết nối với CrewAI... (Phần này chúng ta sẽ code ở bước tiếp theo)")

    elif menu_selection == "📁 Lịch sử tài liệu":
        st.title("📁 Kho lưu trữ cá nhân")
        st.info("Danh sách CV và Cover Letter bạn đã tạo sẽ xuất hiện ở đây.")
