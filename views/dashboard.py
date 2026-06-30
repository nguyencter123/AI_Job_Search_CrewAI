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

    if "AI" in search_mode:
        engine = JobSearchEngine(AiMatchingStrategy())
    else:
        engine = JobSearchEngine(BasicMatchingStrategy())

    if "Tìm nhanh" in search_mode:
        display_jobs, _ = engine.search(user_id, all_jobs, search_kw, search_loc, search_salary)
        st.caption(f"Đang hiển thị {len(display_jobs)}/{len(all_jobs)} công việc")
        st.session_state.pop("ai_sorted_jobs", None)

    else:
        analyze_btn = st.button("✨ Bắt đầu phân tích bằng AI", type="primary", use_container_width=True)
        loading_placeholder = st.empty()

        if analyze_btn:
            with loading_placeholder.container():
                with st.spinner(
                    "🧠 AI đang đọc hồ sơ và chấm điểm hàng loạt công việc... Vui lòng không thao tác gì thêm!"
                ):
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

        # --- HIỂN THỊ QUOTA AI / HUY HIỆU PRO ---
        from services.ai_quota_service import get_user_quota
        quota = get_user_quota(user_id)
        if quota:
            if quota["is_pro"]:
                expiry = quota.get("pro_expiry_date", "")
                expiry_text = f"<p style='text-align: center; font-size: 12px; color: #92400e; margin: 2px 0 0 0;'>Hết hạn: {expiry}</p>" if expiry else ""
                st.markdown(
                    "<div style='text-align: center; background: linear-gradient(135deg, #f59e0b, #d97706); "
                    "color: white; padding: 8px; border-radius: 8px; font-weight: 700; margin: 5px 0;'>"
                    "👑 PRO MEMBER</div>"
                    + expiry_text,
                    unsafe_allow_html=True
                )
            else:
                cv_remain = max(0, quota['cv_limit'] - quota['cv_used'])
                match_remain = max(0, quota['match_limit'] - quota['match_used'])
                st.markdown(
                    f"<div style='text-align: center; background-color: #f1f5f9; "
                    f"padding: 8px; border-radius: 8px; margin: 5px 0; font-size: 13px;'>"
                    f"🤖 AI CV: <b>{cv_remain}/{quota['cv_limit']}</b> lượt &nbsp;|&nbsp; "
                    f"🔍 AI Match: <b>{match_remain}/{quota['match_limit']}</b> lượt</div>",
                    unsafe_allow_html=True
                )

        st.divider()

        menu_items = ["🏠 Trang chủ", "👤 Hồ sơ cá nhân", "🤖 AI Tìm việc & Soạn CV", "📁 Lịch sử tài liệu"]
        # Chỉ hiện tab Nâng cấp cho tài khoản Free
        if quota and not quota["is_pro"]:
            menu_items.append("⭐ Nâng cấp Pro")

        menu_selection = st.radio(
            "📍 Điều hướng",
            menu_items,
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
        from services.user_service import upload_avatar, get_avatar, update_contact

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

        # --- THÔNG TIN LIÊN HỆ (Email + SĐT) ---
        st.markdown("#### 📞 Thông tin liên hệ")
        with st.form("update_contact_form"):
            new_email = st.text_input(
                "📧 Email",
                value=user_info.get("email", ""),
                placeholder="Nhập email liên hệ...",
            )
            new_phone = st.text_input(
                "📱 Số điện thoại",
                value=user_info.get("phone_number", ""),
                placeholder="Nhập số điện thoại liên hệ...",
            )
            
            if st.form_submit_button("💾 Lưu thông tin liên hệ"):
                success, error = update_contact(user_id, new_email.strip(), new_phone.strip())
                if success:
                    st.success("Đã cập nhật thông tin liên hệ!")
                    st.rerun()
                else:
                    st.error(error)

        st.divider()

        # --- CÀI ĐẶT THÔNG BÁO ---
        st.markdown("#### 🔔 Cài đặt thông báo")
        from services.user_service import toggle_receive_email, toggle_receive_telegram, set_telegram_chat_id
        
        col_email, col_tele = st.columns(2)
        with col_email:
            st.markdown("##### 📧 Qua Email")
            current_status = user_info.get("receive_daily_email", False)
            new_status = st.toggle("Nhận email việc làm hàng ngày", value=current_status)
            
            if new_status != current_status:
                if toggle_receive_email(user_id, new_status):
                    st.success("Đã cập nhật!")
                    st.rerun()

        with col_tele:
            st.markdown("##### ✈️ Qua Telegram (Bot)")
            
            # Toggle cho Telegram
            current_tele_status = user_info.get("receive_daily_telegram", False)
            new_tele_status = st.toggle("Nhận Telegram việc làm hàng ngày", value=current_tele_status)
            if new_tele_status != current_tele_status:
                if toggle_receive_telegram(user_id, new_tele_status):
                    st.success("Đã cập nhật trạng thái Telegram!")
                    st.rerun()
            
            st.caption("Bấm [@userinfobot](https://t.me/userinfobot) rồi ấn Start để lấy ID của bạn.")
            
            with st.form("update_telegram_form"):
                current_tele_id = user_info.get("telegram_chat_id", "")
                new_tele_id = st.text_input(
                    "Telegram Chat ID",
                    value=current_tele_id,
                    placeholder="VD: 123456789"
                )
                if st.form_submit_button("Lưu ID"):
                    if set_telegram_chat_id(user_id, new_tele_id.strip()):
                        st.success("Đã cập nhật Telegram ID!")
                        st.rerun()

        st.divider()

        # --- KỸ NĂNG & KINH NGHIỆM ---
        st.markdown("#### 💼 Kỹ năng & Kinh nghiệm")
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

            if st.form_submit_button("💾 Cập nhật kỹ năng & kinh nghiệm"):
                success, error = update_profile(user_id, new_skills, new_exp)
                if success:
                    st.success("Đã cập nhật hồ sơ thành công!")
                else:
                    st.error(error)

    elif menu_selection == "🤖 AI Tìm việc & Soạn CV":
        st.title("🤖 Trợ lý AI — Tạo CV chuyên nghiệp")
        st.write("AI sẽ viết lại nội dung CV của bạn cho chuyên nghiệp hơn, dựa trên hồ sơ cá nhân và mô tả công việc (JD) bạn đang ứng tuyển.")

        job_context = st.session_state.get("selected_job", None)

        if job_context:
            st.success(
                f"Đang chuẩn bị hồ sơ cho vị trí: **{job_context['title']}** tại **{job_context['company']}**"
            )

        jd_default = ""
        if job_context:
            jd_default = job_context.get("full_jd") or job_context.get("short_desc") or ""

        jd_input = st.text_area(
            "📋 Dán Mô tả công việc (JD) vào đây:",
            value=jd_default,
            height=200,
            placeholder="Dán nội dung JD công việc bạn muốn ứng tuyển để AI tối ưu CV phù hợp nhất..."
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            ai_cv_btn = st.button("🚀 Tạo CV bằng AI", type="primary", use_container_width=True)
        with col_btn2:
            raw_cv_btn = st.button("📝 Tạo CV từ hồ sơ (không AI)", use_container_width=True)

        # === XỬ LÝ TẠO CV ===
        if ai_cv_btn or raw_cv_btn:
            use_ai = ai_cv_btn  # True nếu bấm nút AI, False nếu bấm nút thường

            if use_ai and not jd_input.strip():
                st.warning("⚠️ Vui lòng dán Mô tả công việc (JD) để AI có thể tối ưu CV cho bạn!")
            else:
                from services.cv_service import generate_cv

                with st.spinner("🧠 Đang xây dựng CV..." if not use_ai else "🧠 AI đang phân tích và viết CV chuyên nghiệp..."):
                    job_id = job_context.get("id") if job_context else 0
                    html_cv, error = generate_cv(user_id, jd_text=jd_input, use_ai=use_ai, job_id=job_id)

                if error:
                    st.error(f"❌ {error}")
                else:
                    st.session_state["generated_cv_html"] = html_cv
                    st.success("🎉 Tạo CV thành công!")

        # === HIỂN THỊ KẾT QUẢ CV ===
        cv_html = st.session_state.get("generated_cv_html", None)
        if cv_html:
            st.divider()
            st.markdown("### 📄 CV của bạn")

            # Hướng dẫn lưu PDF
            st.info("💡 **Mẹo lưu PDF:** Tải file HTML bên dưới, mở bằng trình duyệt Chrome/Edge và nhấn **Ctrl + P** (chọn 'Save as PDF' / 'Lưu dưới dạng PDF'). Mẫu CV đã được tối ưu chuẩn khổ giấy A4!")

            # Nút tải về
            st.download_button(
                label="⬇️ Tải CV (Định dạng HTML)",
                data=cv_html,
                file_name="CV_AI_Generated.html",
                mime="text/html",
                use_container_width=True,
            )

            # Render HTML trực tiếp lên UI để xem trước
            import streamlit.components.v1 as components
            with st.container(border=True):
                components.html(cv_html, height=800, scrolling=True)

    elif menu_selection == "⭐ Nâng cấp Pro":
        st.title("⭐ Nâng cấp tài khoản Pro")
        st.write("Mở khóa toàn bộ sức mạnh AI — Tạo CV và Phân tích công việc **không giới hạn** mỗi ngày!")

        # ========== BƯỚC 1: CHỌN GÓI ==========
        st.markdown("### 📋 Bước 1: Chọn gói Pro")
        from services.ai_quota_service import PRO_PLANS

        plan_cols = st.columns(len(PRO_PLANS))
        for i, plan in enumerate(PRO_PLANS):
            with plan_cols[i]:
                # Gói 1 năm có viền nổi bật hơn (Best value)
                if plan["months"] == 12:
                    border_style = "border: 2px solid #f59e0b;"
                    badge = "<span style='background: #f59e0b; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;'>Tiết kiệm nhất</span><br>"
                else:
                    border_style = "border: 1px solid #e2e8f0;"
                    badge = ""

                st.markdown(
                    f"<div style='background: #f8fafc; padding: 20px; border-radius: 12px; {border_style} text-align: center;'>"
                    f"{badge}"
                    f"<h4 style='margin-top: 5px;'>📦 {plan['name']}</h4>"
                    f"<p style='font-size: 26px; font-weight: 700; color: #d97706;'>{plan['price']:,} VNĐ</p>"
                    f"<p style='color: #64748b; font-size: 13px;'>≈ {plan['price'] // plan['months']:,} VNĐ/tháng</p>"
                    "</div>",
                    unsafe_allow_html=True
                )

        plan_labels = [f"📦 {p['name']} — {p['price']:,} VNĐ" for p in PRO_PLANS]
        selected_plan_label = st.radio(
            "Chọn gói",
            plan_labels,
            horizontal=True,
            label_visibility="collapsed",
        )
        selected_plan = PRO_PLANS[plan_labels.index(selected_plan_label)]

        st.divider()

        # ========== BƯỚC 2: CHỌN PHƯƠNG THỨC THANH TOÁN (Strategy Pattern) ==========
        st.markdown("### 💳 Bước 2: Chọn phương thức thanh toán")
        from services.payment.payment_context import PaymentContext

        available = PaymentContext.get_available_methods()
        method_labels = [f"{m['icon']} {m['name']}" for m in available]
        method_keys = [m['key'] for m in available]

        selected_method_label = st.radio(
            "Chọn cổng thanh toán",
            method_labels,
            horizontal=True,
            label_visibility="collapsed"
        )
        selected_key = method_keys[method_labels.index(selected_method_label)]

        # Hiển thị thông tin thanh toán từ Strategy
        amount = selected_plan["price"]
        context = PaymentContext(selected_key)
        payment_info = context.get_payment_info(amount)

        with st.container(border=True):
            st.markdown(f"#### {payment_info['icon']} Thanh toán qua {payment_info['name']}")
            st.markdown(f"**Gói đã chọn:** 📦 {selected_plan['name']}  •  **Số tiền:** `{amount:,} VNĐ`")
            st.markdown("---")
            
            # Chia 2 cột: 1 bên hiển thị mã QR, 1 bên hướng dẫn
            col_qr, col_inst = st.columns([1.5, 2])
            with col_qr:
                import qrcode
                from io import BytesIO
                
                # Tạo mã QR từ qr_data của Strategy
                qr = qrcode.QRCode(box_size=8, border=2)
                qr.add_data(payment_info["qr_data"])
                qr.make(fit=True)
                
                # Tô màu QR code theo màu đặc trưng của từng ví
                fill_color = payment_info.get("color", "black")
                img = qr.make_image(fill_color=fill_color, back_color="white")
                
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.image(buf.getvalue(), caption=f"Mã QR {payment_info['name']}", use_container_width=True)
                
            with col_inst:
                st.markdown("**Hướng dẫn chuyển khoản:**")
                for step in payment_info["instructions"]:
                    st.markdown(step)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("✅ Tôi đã thanh toán — Nâng cấp ngay!", type="primary", use_container_width=True):
            result = context.confirm_payment(amount)
            if result.success:
                from services.ai_quota_service import upgrade_to_pro
                success, error = upgrade_to_pro(user_id, months=selected_plan["months"])
                if success:
                    st.success(result.message)
                    st.balloons()
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning(error)
            else:
                st.error(result.message)
    elif menu_selection == "📁 Lịch sử tài liệu":
        st.title("📁 Kho lưu trữ cá nhân")
        st.info("Danh sách CV và Cover Letter bạn đã tạo sẽ xuất hiện ở đây.")
        
        from repositories.database import db_session
        from repositories.models import ApplicationDocument, Job
        from repositories.user_repo import get_user_and_profile
        import base64
        
        with db_session() as db:
            docs = db.query(ApplicationDocument).filter(ApplicationDocument.user_id == user_id).order_by(ApplicationDocument.created_at.desc()).all()
            
            # Lấy ảnh đại diện để "vá" vào CV
            _, profile = get_user_and_profile(db, user_id)
            avatar_b64 = ""
            if profile and profile.avatar_data:
                avatar_b64 = base64.b64encode(profile.avatar_data).decode("utf-8")
            
            if not docs:
                st.write("Bạn chưa tạo CV nào. Hãy dùng tính năng **AI Tìm việc & Soạn CV** để tạo ngay nhé!")
            else:
                st.write(f"Bạn có tổng cộng **{len(docs)}** tài liệu đã tạo.")
                st.divider()
                
                for idx, doc in enumerate(docs):
                    # Lấy tên công việc nếu có
                    job_title = "Vị trí Tự do"
                    if doc.job_id:
                        job = db.query(Job).filter(Job.id == doc.job_id).first()
                        if job:
                            job_title = f"{job.title} ({job.company})"
                    
                    created_date = doc.created_at.strftime("%d/%m/%Y %H:%M")
                    
                    # Khôi phục ảnh đại diện thật từ Placeholder
                    full_cv_html = doc.cv_content.replace("[[AVATAR_PLACEHOLDER]]", avatar_b64)
                    
                    with st.expander(f"📄 CV cho: {job_title} - {created_date}"):
                        col_view, col_dl = st.columns(2)
                        with col_dl:
                            st.download_button(
                                label="⬇️ Tải file HTML",
                                data=full_cv_html,
                                file_name=f"CV_{job_title.replace(' ', '_')}_{idx}.html",
                                mime="text/html",
                                use_container_width=True,
                                key=f"dl_btn_{doc.id}"
                            )
                        with col_view:
                            if st.button("👀 Xem trước CV này", use_container_width=True, key=f"view_btn_{doc.id}"):
                                st.session_state[f"view_doc_{doc.id}"] = True
                                
                        if st.session_state.get(f"view_doc_{doc.id}", False):
                            st.components.v1.html(full_cv_html, height=800, scrolling=True)

