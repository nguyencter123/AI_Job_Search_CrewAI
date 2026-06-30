# File: views/auth_ui.py
import streamlit as st

from services.user_service import login, register


def apply_custom_css():
    """Hàm tiêm CSS tùy chỉnh vào Streamlit để làm đẹp giao diện"""
    st.markdown("""
        <style>
        /* Căn giữa tiêu đề và dòng mô tả */
        h1, p {
            text-align: center !important;
            color: #0f172a;
        }
        
        /* Căn giữa và làm nổi bật container chính chứa các Tab */
        .stTabs {
            background-color: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            border: 1px solid #e2e8f0;
            margin-top: 30px;
        }

        /* Làm đẹp các Tab */
        .stTabs [data-baseweb="tab-list"] {
            gap: 15px;
            border-bottom: 2px solid #e2e8f0;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            border-radius: 8px 8px 0px 0px;
            padding: 10px 24px;
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            border-bottom: none;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #e0f2fe !important;
            color: #0284c7 !important;
            border-bottom: 3px solid #0284c7 !important;
        }
        
        /* Làm đẹp Ô nhập liệu (Text Input) và hiệu ứng Focus */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            padding: 12px 16px;
            transition: all 0.2s ease-in-out;
            font-size: 16px;
        }
        .stTextInput > div > div > input:focus {
            border-color: #38bdf8;
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.3);
            outline: none;
        }
        
        /* Làm đẹp nút Password visibility toggle */
        .stTextInput > div > div > div > button {
            color: #64748b;
        }
        
        /* Làm đẹp Nút bấm (Button) chính và hiệu ứng Hover */
        div.stButton > button:first-child {
            background-color: #0ea5e9;
            color: white;
            border-radius: 8px;
            padding: 12px 24px;
            border: none;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
            width: 100%;
            font-weight: 700;
            margin-top: 20px;
            font-size: 18px;
            cursor: pointer;
        }
        div.stButton > button:first-child:hover {
            background-color: #0284c7;
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        div.stButton > button:first-child:active {
            transform: translateY(0);
        }
        

        
        /* Làm cho giao diện tổng thể sạch sẽ hơn */
        #MainMenu, footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)


def render_auth_page():
    apply_custom_css()
    
    st.markdown("<h1>🚀 Hệ thống Hỗ trợ Ứng tuyển AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin-bottom: 40px;'>Vui lòng đăng nhập hoặc tạo tài khoản để tiếp tục trải nghiệm.</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký"])

        with tab1:
            st.markdown("<h3 style='text-align: center; color: #0f172a; margin-top: 20px;'>Đăng nhập vào hệ thống</h3>", unsafe_allow_html=True)
            
            # --- CHỌN PHƯƠNG THỨC ĐĂNG NHẬP ---
            login_method = st.radio(
                "Phương thức đăng nhập",
                options=["📧 Email", "📱 Số điện thoại"],
                horizontal=True,
                label_visibility="collapsed",
                key="login_method"
            )
            
            if "Email" in login_method:
                login_identifier = st.text_input("Email", key="login_email", placeholder="Nhập email của bạn...")
                login_pass = st.text_input("Mật khẩu", type="password", key="login_pass")
                
                if st.button("Đăng nhập", type="primary", key="login_btn_email"):
                    user_id, role, error = login(method="email", email=login_identifier, password=login_pass)
                    if error:
                        st.error(error)
                    else:
                        st.success("Đăng nhập thành công!")
                        st.session_state["user_id"] = user_id
                        st.session_state["role"] = role
                        st.rerun()
            else:
                login_phone = st.text_input("Số điện thoại", key="login_phone", placeholder="Nhập số điện thoại...")
                login_pass_phone = st.text_input("Mật khẩu", type="password", key="login_pass_phone")
                
                if st.button("Đăng nhập", type="primary", key="login_btn_phone"):
                    user_id, role, error = login(method="phone", phone=login_phone, password=login_pass_phone)
                    if error:
                        st.error(error)
                    else:
                        st.success("Đăng nhập thành công!")
                        st.session_state["user_id"] = user_id
                        st.session_state["role"] = role
                        st.rerun()


        with tab2:
            st.markdown("<h3 style='text-align: center; color: #0f172a; margin-top: 20px;'>Tạo tài khoản mới</h3>", unsafe_allow_html=True)
            
            # --- CHỌN LOẠI TÀI KHOẢN ---
            st.markdown("<p style='font-weight: 600; margin-bottom: 5px; text-align: left;'>Loại tài khoản:</p>", unsafe_allow_html=True)
            role_choice = st.radio(
                "Loại tài khoản",
                options=["👤 Người tìm việc", "🏢 Nhà tuyển dụng"],
                label_visibility="collapsed",
                horizontal=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- CHỌN PHƯƠNG THỨC ĐĂNG KÝ ---
            reg_method = st.radio(
                "Đăng ký bằng",
                options=["📧 Email", "📱 Số điện thoại"],
                horizontal=True,
                label_visibility="collapsed",
                key="reg_method"
            )
            
            selected_role = 'user' if "Người tìm việc" in role_choice else 'job_poster'
            
            if "Email" in reg_method:
                reg_fullname = st.text_input("Họ và Tên (Hoặc tên công ty)", key="reg_name_email")
                reg_email = st.text_input("Email đăng ký", key="reg_email")
                reg_pass = st.text_input("Mật khẩu", type="password", key="reg_pass_email")
                reg_pass_confirm = st.text_input("Xác nhận Mật khẩu", type="password", key="reg_pass_confirm_email")
                
                if st.button("Đăng ký tài khoản", key="reg_btn_email"):
                    user_id, role, error = register(
                        method="email",
                        full_name=reg_fullname,
                        email=reg_email,
                        password=reg_pass,
                        password_confirm=reg_pass_confirm,
                        role=selected_role
                    )
                    if error:
                        st.error(error)
                    else:
                        st.session_state["user_id"] = user_id
                        st.session_state["role"] = role
                        st.rerun()
            else:
                reg_fullname_phone = st.text_input("Họ và Tên (Hoặc tên công ty)", key="reg_name_phone")
                reg_phone = st.text_input("Số điện thoại đăng ký", key="reg_phone")
                reg_pass_phone = st.text_input("Mật khẩu", type="password", key="reg_pass_phone")
                reg_pass_confirm_phone = st.text_input("Xác nhận Mật khẩu", type="password", key="reg_pass_confirm_phone")
                
                if st.button("Đăng ký tài khoản", key="reg_btn_phone"):
                    user_id, role, error = register(
                        method="phone",
                        full_name=reg_fullname_phone,
                        phone=reg_phone,
                        password=reg_pass_phone,
                        password_confirm=reg_pass_confirm_phone,
                        role=selected_role
                    )
                    if error:
                        st.error(error)
                    else:
                        st.session_state["user_id"] = user_id
                        st.session_state["role"] = role
                        st.rerun()