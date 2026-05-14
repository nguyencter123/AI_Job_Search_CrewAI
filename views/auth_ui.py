# File: views/auth_ui.py
import streamlit as st
from repositories.database import SessionLocal
from repositories.user_repo import create_user, get_user_by_email
from services.auth_service import verify_password

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
    # Gọi hàm CSS ngay đầu trang
    apply_custom_css()
    
    st.markdown("<h1>🚀 Hệ thống Hỗ trợ Ứng tuyển AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin-bottom: 40px;'>Vui lòng đăng nhập hoặc tạo tài khoản để tiếp tục trải nghiệm.</p>", unsafe_allow_html=True)

    # Dùng st.columns để căn giữa nội dung chính (Dùng tỷ lệ 1:2:1 để cột giữa chiếm 50% và nằm giữa)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Toàn bộ Form sẽ được đặt trong container của st.tabs và CSS sẽ làm nó nổi bật lên
        tab1, tab2 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký"])

        # --- TAB ĐĂNG NHẬP ---
        with tab1:
            st.markdown("<h3 style='text-align: center; color: #0f172a; margin-top: 20px;'>Đăng nhập vào hệ thống</h3>", unsafe_allow_html=True)
            login_email = st.text_input("Email", key="login_email" )
            login_pass = st.text_input("Mật khẩu", type="password", key="login_pass")
            
            # Đặt nút Đăng nhập vào một container riêng để CSS dễ nhắm mục tiêu
            st.markdown("<div class='login-button-container'>", unsafe_allow_html=True)
            if st.button("Đăng nhập", type="primary"):
                if not login_email or not login_pass:
                    st.warning("Vui lòng nhập đầy đủ Email và Mật khẩu!")
                else:
                    db = SessionLocal()
                    try:
                        user = get_user_by_email(db, login_email)
                        if user and verify_password(login_pass, user.password_hash):
                            st.success("Đăng nhập thành công!")
                            st.session_state['user_id'] = user.id
                            st.session_state['role'] = user.role
                            st.rerun() 
                        else:
                            st.error("Sai Email hoặc Mật khẩu!")
                    finally:
                        db.close()
            st.markdown("</div>", unsafe_allow_html=True)

        # --- TAB ĐĂNG KÝ ---
        with tab2:
            st.markdown("<h3 style='text-align: center; color: #0f172a; margin-top: 20px;'>Tạo tài khoản mới</h3>", unsafe_allow_html=True)
            reg_fullname = st.text_input("Họ và Tên" )
            reg_email = st.text_input("Email đăng ký")
            reg_pass = st.text_input("Mật khẩu", type="password", key="reg_pass")
            reg_pass_confirm = st.text_input("Xác nhận Mật khẩu", type="password")
            
            st.markdown("<div class='register-button-container'>", unsafe_allow_html=True)
            if st.button("Đăng ký tài khoản"):
                if not reg_fullname or not reg_email or not reg_pass:
                    st.warning("Vui lòng điền đầy đủ thông tin!")
                elif reg_pass != reg_pass_confirm:
                    st.error("Mật khẩu xác nhận không khớp!")
                else:
                    db = SessionLocal()
                    try:
                        new_user = create_user(db, reg_email, reg_pass, reg_fullname)
                        if new_user:
                            # THAY ĐỔI Ở ĐÂY: Tự động đăng nhập và chuyển trang luôn
                            st.session_state['user_id'] = new_user.id
                            st.session_state['role'] = new_user.role
                            st.rerun() 
                        else:
                            st.error("⚠️ Email này đã được sử dụng. Vui lòng chọn email khác!")
                    finally:
                        db.close()