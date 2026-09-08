from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ResumeIQ API", version="1.0.0")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to ResumeIQ API"}

# Include routers
from .routers import resume, ats, optimization, intelligence
from .resume_jd.router import router as resume_jd_router
app.include_router(resume.router)
app.include_router(ats.router)
app.include_router(optimization.router)
app.include_router(intelligence.router)
app.include_router(resume_jd_router)
