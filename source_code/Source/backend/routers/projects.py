import logging
import uuid
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, Project, PaperSection, ProjectReference, DocumentSpan, InlineCitation
from backend.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse,
    PaperSectionCreate, PaperSectionUpdate, PaperSectionResponse,
    ProjectReferenceCreate, ProjectReferenceResponse
)
from backend.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/projects",
    tags=["Academic Studio Projects"]
)

DEFAULT_SECTIONS = [
    ("Abstract", "abstract", 0, "## Abstract\n\nWrite your paper abstract here summarizing background, approach, key findings, and contributions."),
    ("Introduction", "introduction", 1, "## 1. Introduction\n\nIntroduce the domain problem, motivation, limitations of prior work, and clear list of primary contributions."),
    ("Related Work", "related-work", 2, "## 2. Related Work\n\nReview existing methodologies and position this work in the literature with accurate citations."),
    ("Methodology", "methodology", 3, "## 3. Methodology\n\nDetail the proposed architectural formulation, algorithms, mathematical definitions, and system parameters."),
    ("Experiments and Results", "experiments", 4, "## 4. Experiments and Results\n\nPresent experimental setup, baseline comparisons, ablation studies, and qualitative analysis with tables and figures."),
    ("Conclusion", "conclusion", 5, "## 5. Conclusion\n\nSummarize findings, practical implications, and future research directions.")
]

@router.get("", response_model=List[ProjectResponse])
def get_user_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all academic paper projects created by the authenticated user."""
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.updated_at.desc()).all()
    return projects

@router.post("", response_model=ProjectDetailResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new academic paper project and initialize standard IEEE/ACM paper sections."""
    new_project = Project(
        user_id=current_user.id,
        title=project_in.title,
        template_type=project_in.template_type or "ieee_conference",
        target_venue=project_in.target_venue,
        primary_domain=project_in.primary_domain or "it",
        abstract_text=project_in.abstract_text or "",
        keywords=project_in.keywords or []
    )
    db.add(new_project)
    db.flush()

    # Seed standard sections for immediate writing
    for title, slug, idx, content in DEFAULT_SECTIONS:
        sec = PaperSection(
            project_id=new_project.id,
            title=title,
            slug=slug,
            order_index=idx,
            content_markdown=content,
            word_count=len(content.split())
        )
        db.add(sec)

    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project_detail(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch complete academic project details including all sections and attached references."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure sections are ordered by order_index
    project.sections.sort(key=lambda s: s.order_index)
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project metadata such as title, venue, or abstract."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an academic project and cascade delete all associated sections and references."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return None

# --- SECTION MANAGEMENT (AUTO-SAVE SYNC) ---

@router.get("/{project_id}/sections", response_model=List[PaperSectionResponse])
def list_sections(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all sections of a project ordered by order_index."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    sections = db.query(PaperSection).filter(PaperSection.project_id == project_id).order_by(PaperSection.order_index).all()
    return sections

@router.post("/{project_id}/sections", response_model=PaperSectionResponse, status_code=status.HTTP_201_CREATED)
def create_section(
    project_id: UUID,
    section_in: PaperSectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new section to an academic project."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    slug = section_in.slug or section_in.title.lower().replace(" ", "-")
    content = section_in.content_markdown or ""
    new_sec = PaperSection(
        project_id=project_id,
        title=section_in.title,
        slug=slug,
        order_index=section_in.order_index or 0,
        content_markdown=content,
        word_count=len(content.split())
    )
    db.add(new_sec)
    db.commit()
    db.refresh(new_sec)
    return new_sec

@router.put("/{project_id}/sections/{section_id}", response_model=PaperSectionResponse)
def update_section(
    project_id: UUID,
    section_id: UUID,
    section_in: PaperSectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update section content and markdown. Used by auto-save sync in Academic Editor."""
    section = db.query(PaperSection).filter(
        PaperSection.id == section_id,
        PaperSection.project_id == project_id
    ).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    update_data = section_in.dict(exclude_unset=True)
    if "content_markdown" in update_data and update_data["content_markdown"] is not None:
        words = len(update_data["content_markdown"].split())
        section.word_count = words

    for key, value in update_data.items():
        setattr(section, key, value)

    section.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(section)
    return section

@router.delete("/{project_id}/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(
    project_id: UUID,
    section_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a section from a project."""
    section = db.query(PaperSection).filter(
        PaperSection.id == section_id,
        PaperSection.project_id == project_id
    ).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    db.delete(section)
    db.commit()
    return None

# --- REFERENCES MANAGEMENT ---

@router.get("/{project_id}/references", response_model=List[ProjectReferenceResponse])
def list_references(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all bibliographical references attached to a project."""
    refs = db.query(ProjectReference).filter(ProjectReference.project_id == project_id).order_by(ProjectReference.created_at).all()
    return refs

@router.post("/{project_id}/references", response_model=ProjectReferenceResponse, status_code=status.HTTP_201_CREATED)
def attach_reference(
    project_id: UUID,
    ref_in: ProjectReferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Attach a bibliographical paper reference (BibTeX) to the project."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_ref = ProjectReference(
        project_id=project_id,
        bibtex_key=ref_in.bibtex_key,
        title=ref_in.title,
        authors=ref_in.authors,
        year=ref_in.year,
        venue=ref_in.venue,
        doi=ref_in.doi,
        pdf_source_path=ref_in.pdf_source_path,
        bibtex_raw=ref_in.bibtex_raw
    )
    db.add(new_ref)
    db.commit()
    db.refresh(new_ref)
    return new_ref
