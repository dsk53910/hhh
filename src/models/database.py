"""
SQLAlchemy models for HHH Bot database
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
    ForeignKey,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any, List

Base = declarative_base()


class ApplicationStatus(PyEnum):
    """Application status enum"""

    PENDING = "pending"
    SENT = "sent"
    VIEWED = "viewed"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"


class JobSource(PyEnum):
    """Job source enum"""

    HH_RU = "hh.ru"
    OTHER = "other"


class User(Base):
    """User model for bot settings and preferences"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    search_profiles = relationship(
        "SearchProfile", back_populates="user", cascade="all, delete-orphan"
    )
    applications = relationship("JobApplication", back_populates="user")
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"


class SearchProfile(Base):
    """Search profile for job monitoring"""

    __tablename__ = "search_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Search criteria as JSON
    search_criteria = Column(JSON, nullable=False)

    # Scheduling
    search_interval = Column(Integer, default=300)  # seconds
    last_search_at = Column(DateTime, nullable=True)
    next_search_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="search_profiles")
    monitored_jobs = relationship(
        "MonitoredJob", back_populates="search_profile", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<SearchProfile(id={self.id}, name='{self.name}', user_id={self.user_id})>"
        )


class Vacancy(Base):
    """Job vacancy model"""

    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(
        String(50), unique=True, index=True, nullable=False
    )  # External ID from hh.ru
    source = Column(Enum(JobSource), nullable=False, default=JobSource.HH_RU)
    url = Column(Text, nullable=False)

    # Job details
    title = Column(String(500), nullable=False)
    company_name = Column(String(200), nullable=True)
    company_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)

    # Employment details
    salary_from = Column(Integer, nullable=True)
    salary_to = Column(Integer, nullable=True)
    salary_currency = Column(String(10), nullable=True)
    salary_gross = Column(Boolean, nullable=True)

    # Categorical information
    experience = Column(String(50), nullable=True)  # noExperience, between1And3, etc.
    employment_type = Column(String(100), nullable=True)  # full, part, project, etc.
    schedule = Column(String(100), nullable=True)  # remote, office, hybrid, etc.
    work_format = Column(String(50), nullable=True)

    # Location
    area = Column(String(200), nullable=True)
    city = Column(String(200), nullable=True)
    address = Column(Text, nullable=True)

    # Company details
    company_size = Column(String(50), nullable=True)
    industry = Column(String(200), nullable=True)

    # Metadata
    published_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    views_count = Column(Integer, default=0)
    responses_count = Column(Integer, default=0)

    # Internal tracking
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    has_test = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    # Timestamps
    first_seen_at = Column(DateTime, default=func.now())
    last_seen_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Raw data from API
    raw_data = Column(JSON, nullable=True)

    # Relationships
    applications = relationship("JobApplication", back_populates="vacancy")
    monitored_jobs = relationship("MonitoredJob", back_populates="vacancy")

    def __repr__(self):
        return f"<Vacancy(id={self.id}, vacancy_id='{self.vacancy_id}', title='{self.title[:50]}')>"


class MonitoredJob(Base):
    """Association table for search profiles and vacancies they're monitoring"""

    __tablename__ = "monitored_jobs"

    id = Column(Integer, primary_key=True, index=True)
    search_profile_id = Column(
        Integer, ForeignKey("search_profiles.id"), nullable=False
    )
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)

    # Status and tracking
    is_notified = Column(Boolean, default=False)
    notified_at = Column(DateTime, nullable=True)
    is_matched = Column(Boolean, default=True)  # Whether job matches criteria
    match_score = Column(Integer, default=0)  # How well it matches criteria

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    search_profile = relationship("SearchProfile", back_populates="monitored_jobs")
    vacancy = relationship("Vacancy", back_populates="monitored_jobs")

    def __repr__(self):
        return f"<MonitoredJob(search_profile_id={self.search_profile_id}, vacancy_id={self.vacancy_id})>"


class JobApplication(Base):
    """Job application tracking"""

    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)

    # Application details
    status = Column(
        Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False
    )
    response_text = Column(Text, nullable=True)  # Response text sent
    cover_letter = Column(Text, nullable=True)

    # Auto-apply information
    is_auto_applied = Column(Boolean, default=False)
    auto_apply_profile = Column(String(100), nullable=True)
    approval_required = Column(Boolean, default=True)
    approved_at = Column(DateTime, nullable=True)

    # Timeline
    applied_at = Column(DateTime, nullable=True)
    viewed_by_employer_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)

    # Notes and tracking
    notes = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)

    # External tracking
    external_application_id = Column(String(100), nullable=True)
    application_url = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="applications")
    vacancy = relationship("Vacancy", back_populates="applications")

    def __repr__(self):
        return f"<JobApplication(id={self.id}, status='{self.status}', vacancy_id={self.vacancy_id})>"


class Notification(Base):
    """Notification tracking"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Notification content
    message_type = Column(
        String(50), nullable=False
    )  # new_job, application_update, digest, etc.
    title = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)

    # Delivery tracking
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    delivery_method = Column(String(50), nullable=True)  # telegram, email, etc.

    # Related entities
    related_vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=True)
    related_application_id = Column(
        Integer, ForeignKey("job_applications.id"), nullable=True
    )

    # Additional data
    data = Column(JSON, nullable=True)  # Additional notification data

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")
    related_vacancy = relationship("Vacancy")
    related_application = relationship("JobApplication")

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.message_type}', sent={self.is_sent})>"


class SearchStatistics(Base):
    """Search statistics and analytics"""

    __tablename__ = "search_statistics"

    id = Column(Integer, primary_key=True, index=True)
    search_profile_id = Column(
        Integer, ForeignKey("search_profiles.id"), nullable=False
    )

    # Search metrics
    search_date = Column(DateTime, nullable=False)
    total_found = Column(Integer, default=0)
    new_jobs = Column(Integer, default=0)
    applications_sent = Column(Integer, default=0)

    # Performance metrics
    search_duration = Column(Integer, nullable=True)  # milliseconds
    api_requests_count = Column(Integer, default=0)

    # Additional data
    search_criteria = Column(JSON, nullable=True)
    top_keywords = Column(JSON, nullable=True)  # Most common keywords in results

    # Timestamps
    created_at = Column(DateTime, default=func.now())

    # Relationships
    search_profile = relationship("SearchProfile")

    def __repr__(self):
        return f"<SearchStatistics(id={self.id}, date={self.search_date}, total_found={self.total_found})>"


class SystemSettings(Base):
    """System-wide settings and configuration"""

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)

    # Metadata
    is_encrypted = Column(Boolean, default=False)
    category = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SystemSettings(key='{self.key}', value={self.value})>"
