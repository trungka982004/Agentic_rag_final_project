import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("Profile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False, default="New Conversation")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user' or 'agent'
    content = Column(Text, nullable=False)
    export_links = Column(JSON, nullable=True)  # e.g., {"docs": "url", "sheets": "url"}
    flags = Column(JSON, nullable=True)         # e.g., {"expert_required": True, "python_repl": False}
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    org = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="profile")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    template_type = Column(String(50), nullable=False, default="ieee_conference")
    target_venue = Column(String(255), nullable=True)
    primary_domain = Column(String(50), nullable=False, default="it")
    abstract_text = Column(Text, nullable=True, default="")
    keywords = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="projects")
    sections = relationship("PaperSection", back_populates="project", cascade="all, delete-orphan", order_by="PaperSection.order_index")
    references = relationship("ProjectReference", back_populates="project", cascade="all, delete-orphan")


class PaperSection(Base):
    __tablename__ = "paper_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    content_markdown = Column(Text, nullable=False, default="")
    content_latex = Column(Text, nullable=False, default="")
    word_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="sections")
    citations = relationship("InlineCitation", back_populates="section", cascade="all, delete-orphan")


class ProjectReference(Base):
    __tablename__ = "project_references"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    bibtex_key = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    authors = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    venue = Column(String(255), nullable=True)
    doi = Column(String(100), nullable=True)
    pdf_source_path = Column(String(500), nullable=True)
    bibtex_raw = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="references")
    citations = relationship("InlineCitation", back_populates="reference")


class DocumentSpan(Base):
    __tablename__ = "document_spans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain = Column(String(50), nullable=False, index=True)
    document_name = Column(String(255), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    bbox_x0 = Column(Float, nullable=False)
    bbox_y0 = Column(Float, nullable=False)
    bbox_x1 = Column(Float, nullable=False)
    bbox_y1 = Column(Float, nullable=False)
    text_content = Column(Text, nullable=False)
    chunk_id = Column(String(100), nullable=True, index=True)

    # Relationships
    citations = relationship("InlineCitation", back_populates="span")


class InlineCitation(Base):
    __tablename__ = "inline_citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey("paper_sections.id", ondelete="CASCADE"), nullable=False, index=True)
    reference_id = Column(UUID(as_uuid=True), ForeignKey("project_references.id", ondelete="CASCADE"), nullable=False, index=True)
    span_id = Column(UUID(as_uuid=True), ForeignKey("document_spans.id", ondelete="SET NULL"), nullable=True, index=True)
    claim_text = Column(Text, nullable=False)
    similarity_score = Column(Float, nullable=True)
    verification_status = Column(String(50), nullable=False, default="unverified")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    section = relationship("PaperSection", back_populates="citations")
    reference = relationship("ProjectReference", back_populates="citations")
    span = relationship("DocumentSpan", back_populates="citations")
