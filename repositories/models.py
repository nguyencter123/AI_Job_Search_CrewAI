# File: repositories/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, Enum, ForeignKey, LargeBinary, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base 

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    facebook_id = Column(String(100), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    auth_provider = Column(Enum('email', 'phone', 'facebook'), default='email')
    role = Column(Enum('user', 'admin', 'job_poster'), default='user')
    is_active = Column(Boolean, default=True)
    is_pro = Column(Boolean, default=False)                    # Tài khoản Pro (không giới hạn AI)
    pro_expiry_date = Column(Date, nullable=True)              # Ngày hết hạn gói Pro (None = chưa mua)
    cv_ai_usage_count = Column(Integer, default=0)             # Số lần tạo CV bằng AI hôm nay
    match_ai_usage_count = Column(Integer, default=0)          # Số lần dùng AI phân tích Job hôm nay
    last_usage_reset = Column(Date, server_default=func.current_date())  # Ngày reset bộ đếm
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Thiết lập mối quan hệ với các bảng khác để dễ gọi dữ liệu sau này
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    employer_profile = relationship("EmployerProfile", back_populates="user", uselist=False)
    matches = relationship("UserJobMatch", back_populates="user")
    documents = relationship("ApplicationDocument", back_populates="user")
    jobs = relationship("Job", back_populates="poster")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    skills = Column(Text)
    experience_summary = Column(Text)
    avatar_data = Column(LargeBinary(length=2 * 1024 * 1024))  # Ảnh đại diện (tối đa 2MB)
    avatar_mimetype = Column(String(50))  # Loại ảnh: image/jpeg, image/png
    receive_daily_email = Column(Boolean, default=True)
    receive_daily_telegram = Column(Boolean, default=False)
    telegram_chat_id = Column(String(50), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="profile")

class EmployerProfile(Base):
    __tablename__ = "employer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    company_description = Column(Text)
    website = Column(String(255))
    address = Column(String(255))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="employer_profile")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    poster_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    salary = Column(String(100))
    short_desc = Column(Text)
    full_jd = Column(Text)
    contact_email = Column(String(255))
    quantity = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    poster = relationship("User", back_populates="jobs")

class UserJobMatch(Base):
    __tablename__ = "user_job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, nullable=False) # Changed to Integer as jobs.id is Integer now
    job_title = Column(String(255))
    match_score = Column(Float)
    is_emailed = Column(Boolean, default=False)
    matched_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="matches")

class ApplicationDocument(Base):
    __tablename__ = "application_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, nullable=False) # Changed to Integer
    cv_content = Column(Text) 
    cover_letter_content = Column(Text)
    linkedin_message_content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="documents")

class SystemConfig(Base):
    __tablename__ = "system_configs"
    
    config_key = Column(String(50), primary_key=True)
    config_value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())