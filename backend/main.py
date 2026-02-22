from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Optional, List
import os
from datetime import timedelta

from database import create_db_and_tables, get_session
from models import User, Project, Generation
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from service import VoiceGenerator, VOICE_DIR
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for frontend development
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Initialize Voice Generator
try:
    generator = VoiceGenerator()
except Exception as e:
    print(f"Error initializing VoiceGenerator: {e}")
    generator = None

# Mount the static files for demos
DEMO_DIR = os.path.join(VOICE_DIR, "demos")
if not os.path.exists(DEMO_DIR):
    os.makedirs(DEMO_DIR)

app.mount("/demos", StaticFiles(directory=DEMO_DIR), name="demos")

# --- Pydantic Models for Requests ---
class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class GenerateRequest(BaseModel):
    text: str
    target_duration: Optional[float] = 0.0
    speaker: Optional[str] = "p226"
    project_id: Optional[int] = None

class ProjectCreate(BaseModel):
    title: str
    script_content: str

class ProjectRead(BaseModel):
    id: int
    title: str
    script_content: str
    
# --- Auth Endpoints ---

@app.post("/register", response_model=Token)
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pwd)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "id": current_user.id}

# --- Project Endpoints ---

@app.post("/projects", response_model=ProjectRead)
def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    db_project = Project(
        title=project.title, 
        script_content=project.script_content, 
        user_id=current_user.id
    )
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

@app.get("/projects", response_model=List[ProjectRead])
def get_projects(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(Project).where(Project.user_id == current_user.id)
    results = session.exec(statement).all()
    return results

@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}")
def update_project(project_id: int, project_data: ProjectCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.title = project_data.title
    project.script_content = project_data.script_content
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

# --- Generation Endpoints ---

@app.post("/generate")
def generate_voice(
    request: GenerateRequest, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not generator:
        raise HTTPException(status_code=500, detail="Voice Generator not initialized")
    
    try:
        # Generate Audio
        filename = generator.generate(
            text=request.text,
            target_duration=request.target_duration,
            speaker=request.speaker
        )
        
        # Save to DB
        new_gen = Generation(
            filename=filename,
            original_text=request.text,
            duration=request.target_duration, # Note: this is target, not actual. Improve later.
            user_id=current_user.id
        )
        session.add(new_gen)
        session.commit()
        
        return {"filename": filename, "url": f"/download/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generations")
def get_my_generations(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(Generation).where(Generation.user_id == current_user.id).order_by(Generation.created_at.desc())
    results = session.exec(statement).all()
    return results

@app.get("/download/{filename}")
def download_file(filename: str):
    # Security: Ensure we don't allow directory traversal
    if ".." in filename or "/" in filename:
         raise HTTPException(status_code=400, detail="Invalid filename")
         
    file_path = os.path.join(VOICE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="audio/wav", filename=filename)

@app.get("/voices")
def get_voices():
    # Hardcoded list based on VCTK model or known good speakers
    return {
        "voices": [
            {"id": "p226", "name": "Male 1 (p226)", "demo_url": "/demos/p226.wav"},
            {"id": "p259", "name": "Male 2 (p259)", "demo_url": "/demos/p259.wav"},
            {"id": "p247", "name": "Male 3 (p247)", "demo_url": "/demos/p247.wav"},
            {"id": "p260", "name": "Male 4 (p260)", "demo_url": "/demos/p260.wav"},
            {"id": "p245", "name": "Male 5 (p245)", "demo_url": "/demos/p245.wav"},
            {"id": "p230", "name": "Female 1 (p230)", "demo_url": "/demos/p230.wav"}, 
            {"id": "p236", "name": "Female 2 (p236)", "demo_url": "/demos/p236.wav"},
            {"id": "p225", "name": "Speaker 8 (p225)", "demo_url": "/demos/p225.wav"},
            {"id": "p227", "name": "Speaker 9 (p227)", "demo_url": "/demos/p227.wav"},
            {"id": "p228", "name": "Speaker 10 (p228)", "demo_url": "/demos/p228.wav"},
            {"id": "p229", "name": "Speaker 11 (p229)", "demo_url": "/demos/p229.wav"},
            {"id": "p231", "name": "Speaker 12 (p231)", "demo_url": "/demos/p231.wav"},
            {"id": "p232", "name": "Speaker 13 (p232)", "demo_url": "/demos/p232.wav"},
            {"id": "p233", "name": "Speaker 14 (p233)", "demo_url": "/demos/p233.wav"},
            {"id": "p234", "name": "Speaker 15 (p234)", "demo_url": "/demos/p234.wav"},
            {"id": "p237", "name": "Speaker 16 (p237)", "demo_url": "/demos/p237.wav"},
            {"id": "p238", "name": "Speaker 17 (p238)", "demo_url": "/demos/p238.wav"},
            {"id": "p239", "name": "Speaker 18 (p239)", "demo_url": "/demos/p239.wav"},
            {"id": "p240", "name": "Speaker 19 (p240)", "demo_url": "/demos/p240.wav"},
            {"id": "p241", "name": "Speaker 20 (p241)", "demo_url": "/demos/p241.wav"},
            {"id": "p243", "name": "Speaker 21 (p243)", "demo_url": "/demos/p243.wav"},
            {"id": "p244", "name": "Speaker 22 (p244)", "demo_url": "/demos/p244.wav"},
            {"id": "p246", "name": "Speaker 23 (p246)", "demo_url": "/demos/p246.wav"},
            {"id": "p248", "name": "Speaker 24 (p248)", "demo_url": "/demos/p248.wav"},
            {"id": "p249", "name": "Speaker 25 (p249)", "demo_url": "/demos/p249.wav"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
