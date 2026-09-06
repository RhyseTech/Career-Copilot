from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    file_url = Column(String)
    parsed_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ResumeVersion(Base):
    __tablename__ = "resume_versions"
    id = Column(String, primary_key=True, default=generate_uuid)
    resume_id = Column(String, ForeignKey("resumes.id"))
    parent_version_id = Column(String, ForeignKey("resume_versions.id"), nullable=True)
    version_number = Column(Integer)
    content_json = Column(JSON)
    ats_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String)
    company = Column(String)
    content = Column(String)
    extracted_requirements = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
