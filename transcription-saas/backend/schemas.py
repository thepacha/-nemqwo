from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class TranscriptionCreate(BaseModel):
    filename: str
    transcription_text: str
    file_size: int
    duration: Optional[float] = None

class TranscriptionResponse(BaseModel):
    id: int
    filename: str
    transcription_text: str
    file_size: int
    duration: Optional[float]
    created_at: datetime
    
    class Config:
        orm_mode = True

class APIKeyCreate(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class SubscriptionCreate(BaseModel):
    plan_name: str
    price_id: str

class SubscriptionResponse(BaseModel):
    id: int
    plan_name: str
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    monthly_transcription_limit: int
    monthly_transcription_used: int
    created_at: datetime
    
    class Config:
        orm_mode = True