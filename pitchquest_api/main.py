from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import health, sessions, mentor  # ← ADDED: mentor import

app = FastAPI(
    title="PitchQuest API",
    version="1.0.0",
    description="Educational Multi-Agent Pitch Training System"
)

# Add CORS middleware for web frontend later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(mentor.router, prefix="/api/mentor", tags=["mentor"])  # ← ADDED: mentor router

@app.get("/")
async def root():
    return {"message": "PitchQuest API is running!"}