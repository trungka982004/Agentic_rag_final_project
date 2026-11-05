from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

class ProfileResponse(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    org: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    org: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True

# Message schemas
class MessageCreate(BaseModel):
    role: str = Field(..., pattern="^(user|agent)$")
    content: str
    export_links: Optional[Dict[str, Any]] = None
    flags: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    export_links: Optional[Dict[str, Any]] = None
    flags: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ChatSession schemas
class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class ChatSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatSessionDetailResponse(ChatSessionResponse):
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True



# --- ACADEMIC STUDIO SCHEMAS ---

class ProjectBase(BaseModel):
    title: str = Field(..., max_length=500)
    template_type: Optional[str] = "ieee_conference"
    target_venue: Optional[str] = None
    primary_domain: Optional[str] = "it"
    abstract_text: Optional[str] = ""
    keywords: Optional[List[str]] = []

class ProjectCreate(ProjectBase):
    pass

class PaperSectionResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    slug: str
    order_index: int
    content_markdown: str
    content_latex: Optional[str] = ""
    word_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaperSectionCreate(BaseModel):
    title: str
    slug: Optional[str] = None
    order_index: Optional[int] = 0
    content_markdown: Optional[str] = ""

class PaperSectionUpdate(BaseModel):
    title: Optional[str] = None
    content_markdown: Optional[str] = None
    content_latex: Optional[str] = None
    order_index: Optional[int] = None
    word_count: Optional[int] = None

class ProjectReferenceResponse(BaseModel):
    id: UUID
    project_id: UUID
    bibtex_key: str
    title: str
    authors: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    pdf_source_path: Optional[str] = None
    bibtex_raw: str
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectResponse(ProjectBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectDetailResponse(ProjectResponse):
    sections: List[PaperSectionResponse] = []
    references: List[ProjectReferenceResponse] = []

    class Config:
        from_attributes = True

class DocumentSpanResponse(BaseModel):
    id: UUID
    domain: str
    document_name: str
    page_number: int
    bbox_x0: float
    bbox_y0: float
    bbox_x1: float
    bbox_y1: float
    text_content: str
    chunk_id: Optional[str] = None

    class Config:
        from_attributes = True

class InlineCitationResponse(BaseModel):
    id: UUID
    section_id: UUID
    reference_id: UUID
    span_id: Optional[UUID] = None
    claim_text: str
    similarity_score: Optional[float] = None
    verification_status: str
    created_at: datetime

    class Config:
        from_attributes = True
