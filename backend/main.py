from typing import List
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, status
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
