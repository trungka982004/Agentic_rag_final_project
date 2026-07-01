import sys
import os
# Force sys.stdout and sys.stderr to use UTF-8 to prevent cp1252/cp437 encoding errors on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Add parent directory to sys.path to allow importing backend module when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from uuid import UUID
from datetime import datetime
import shutil
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import engine, Base, get_db
from backend.models import User, ChatSession, Message
from backend.schemas import (
    UserCreate, UserResponse, Token,
    ChatSessionCreate, ChatSessionResponse, ChatSessionDetailResponse,
    MessageResponse
)
from backend.auth import (
    get_password_hash, verify_password, create_access_token, get_current_user
)

from backend.routers import chat

# Automatically create tables in PostgreSQL if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agentic RAG Fullstack Backend",
    description="Backend API for the Agentic RAG Web Application with Authentication and Database Persistence.",
    version="1.0.0"
)

# Configure CORS for Next.js or Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Agentic RAG Backend is running successfully!"}

app.include_router(chat.router)

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_pw = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# --- CHAT SESSION ENDPOINTS ---

@app.post("/api/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_in: ChatSessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_session = ChatSession(
        user_id=current_user.id,
        title=session_in.title
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@app.get("/api/sessions", response_model=List[ChatSessionResponse])
def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()
    return sessions

@app.get("/api/sessions/{session_id}", response_model=ChatSessionDetailResponse)
def get_session(session_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return session

@app.delete("/api/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db.delete(session)
    db.commit()
    return

# --- DOCUMENT LIBRARY ENDPOINTS ---

RAW_DATA_PATH = "data/raw"

def get_all_documents():
    docs = []
    if not os.path.exists(RAW_DATA_PATH):
        return docs
        
    # Walk through each domain folder
    for domain in ["it", "math", "physics", "electronics"]:
        domain_path = os.path.join(RAW_DATA_PATH, domain)
        if not os.path.exists(domain_path):
            continue
            
        for file in os.listdir(domain_path):
            if file.endswith(".pdf"):
                file_path = os.path.join(domain_path, file)
                stat = os.stat(file_path)
                size_mb = stat.st_size / (1024 * 1024)
                
                # Format creation/modified time
                added_date = datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y")
                
                # AI Status: check if index folder exists
                domain_db_path = os.path.join("db/vector_stores", f"{domain}_index")
                status = "done" if os.path.exists(domain_db_path) else "pending"
                
                docs.append({
                    "id": file, # use filename as id
                    "name": file,
                    "author": domain.upper(), # Map domain as author/tag for SIS
                    "year": datetime.fromtimestamp(stat.st_mtime).year,
                    "date": added_date,
                    "size": f"{size_mb:.1f} MB",
                    "status": status
                })
    return docs

def run_ingestion_background():
    try:
        from local_rag import clear_rag_caches
        clear_rag_caches()
        from ingestion import ingest_docs
        ingest_docs()
        clear_rag_caches()
    except Exception as e:
        print(f"[Ingestion Background] Error: {e}")

@app.get("/api/documents")
def list_documents(current_user: User = Depends(get_current_user)):
    try:
        return get_all_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/upload")
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    domain: str = Form("it"),
    current_user: User = Depends(get_current_user)
):
    if domain not in ["it", "math", "physics", "electronics"]:
        raise HTTPException(status_code=400, detail="Invalid domain")
        
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    domain_path = os.path.join(RAW_DATA_PATH, domain)
    if not os.path.exists(domain_path):
        os.makedirs(domain_path)
        
    file_path = os.path.join(domain_path, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Trigger background ingestion
        background_tasks.add_task(run_ingestion_background)
        
        return {"message": f"Successfully uploaded {file.filename}. AI analysis started in background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
