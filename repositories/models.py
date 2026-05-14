# File: repositories/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base # Nhập khuôn mẫu Base từ file database.py cùng thư mục

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('user', 'admin'), default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Thiết lập mối quan hệ với các bảng khác để dễ gọi dữ liệu sau này
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    matches = relationship("UserJobMatch", back_populates="user")
    documents = relationship("ApplicationDocument", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    skills = Column(Text)
    experience_summary = Column(Text)
    receive_daily_email = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="profile")

class UserJobMatch(Base):
    __tablename__ = "user_job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String(100), nullable=False)
    job_title = Column(String(255))
    match_score = Column(Float)
    is_emailed = Column(Boolean, default=False)
    matched_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="matches")

class ApplicationDocument(Base):
    __tablename__ = "application_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String(100), nullable=False)
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