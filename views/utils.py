# File: views/utils.py
import streamlit as st

def load_css(file_name: str):
    """Hàm đọc file CSS và nhúng vào Streamlit."""
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            css_code = f.read()
            st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ Không tìm thấy file giao diện: {file_name}")