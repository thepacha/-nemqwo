#!/usr/bin/env python3
"""
VoiceScript AI - Demo Backend
A simplified version for preview without external API dependencies
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
import time
from typing import List, Optional
from datetime import datetime

# Simple in-memory storage for demo
users_db = {}
transcriptions_db = []
api_keys_db = []

app = FastAPI(
    title="VoiceScript AI - Demo",
    description="AI Voice Transcription SaaS - Demo Version",
    version="1.0.0-demo"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool = True
    created_at: datetime

class TranscriptionResponse(BaseModel):
    id: int
    filename: str
    transcription_text: str
    file_size: int
    duration: Optional[float]
    created_at: datetime

class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str
    created_at: datetime

# Demo transcription text
DEMO_TRANSCRIPTIONS = [
    "Hello, this is a demo transcription. The AI has successfully converted your audio file into text.",
    "Welcome to VoiceScript AI! This is an example of how our transcription service works with high accuracy.",
    "This demo shows the power of AI-driven voice transcription. Your audio content is processed quickly and accurately.",
    "Thank you for trying our transcription service. This text represents what would be generated from your audio file.",
    "VoiceScript AI provides fast, accurate, and reliable voice-to-text conversion for all your transcription needs."
]

@app.get("/")
async def root():
    return {
        "message": "VoiceScript AI - Demo Version", 
        "version": "1.0.0-demo",
        "note": "This is a demo version with simulated transcription"
    }

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    # Check if user exists
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = len(users_db) + 1
    users_db[user.email] = {
        "id": user_id,
        "email": user.email,
        "password": user.password,  # In real app, this would be hashed
        "full_name": user.full_name,
        "is_active": True,
        "created_at": datetime.now()
    }
    
    return UserResponse(**users_db[user.email])

@app.post("/auth/login")
async def login(email: str = None, password: str = None):
    user = users_db.get(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Return a simple token (in real app, this would be JWT)
    return {"access_token": f"demo_token_{user['id']}", "token_type": "bearer"}

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type or not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Simulate processing time
    time.sleep(2)
    
    # Generate demo transcription
    import random
    transcription_text = random.choice(DEMO_TRANSCRIPTIONS)
    
    # Create transcription record
    transcription_id = len(transcriptions_db) + 1
    transcription = {
        "id": transcription_id,
        "filename": file.filename,
        "transcription_text": transcription_text,
        "file_size": file_size,
        "duration": round(file_size / 16000, 2),  # Estimate duration
        "created_at": datetime.now()
    }
    
    transcriptions_db.append(transcription)
    
    return TranscriptionResponse(**transcription)

@app.get("/transcriptions", response_model=List[TranscriptionResponse])
async def get_transcriptions(skip: int = 0, limit: int = 100):
    # Return all transcriptions (in real app, filter by user)
    return [TranscriptionResponse(**t) for t in transcriptions_db[skip:skip+limit]]

@app.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(name: str = "Demo API Key"):
    import uuid
    
    api_key_id = len(api_keys_db) + 1
    api_key = {
        "id": api_key_id,
        "name": name,
        "key": f"tsk_{uuid.uuid4().hex[:24]}",
        "created_at": datetime.now()
    }
    
    api_keys_db.append(api_key)
    return APIKeyResponse(**api_key)

@app.get("/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys():
    return [APIKeyResponse(**key) for key in api_keys_db]

@app.get("/subscriptions/current")
async def get_current_subscription():
    return {
        "id": 1,
        "plan_name": "starter",
        "status": "active",
        "current_period_start": None,
        "current_period_end": None,
        "cancel_at_period_end": False,
        "monthly_transcription_limit": 60,
        "monthly_transcription_used": len(transcriptions_db),
        "created_at": datetime.now()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "transcriptions_count": len(transcriptions_db),
        "users_count": len(users_db)
    }

if __name__ == "__main__":
    print("🚀 Starting VoiceScript AI Demo Server...")
    print("📝 This is a demo version with simulated AI transcription")
    print("🌐 Frontend will be available at: http://localhost:3000")
    print("🔧 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)