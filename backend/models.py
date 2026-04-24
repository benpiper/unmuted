from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    directory_path = Column(String, nullable=False, unique=True)
    video_filename = Column(String)
    total_frames = Column(Integer, default=0)
    fps = Column(Float, default=1.0)
    prompt = Column(Text)
    context = Column(Text)
    tool_context = Column(Text)
    selected_synopsis = Column(Text)
    story_plan = Column(JSON, default=list) # Store as JSON array
    status = Column(String, default="setup") # setup | extracting | review | done
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="projects")
    segments = relationship("TranscriptSegment", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("JobRecord", back_populates="project", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"))
    timestamp = Column(String, nullable=False)
    narration = Column(Text)
    overlay = Column(Text)
    order = Column(Integer)

    project = relationship("Project", back_populates="segments")

class JobRecord(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    status = Column(String) # pending | running | complete | failed | cancelled
    progress = Column(Integer, default=0)
    result = Column(JSON)
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="jobs")
