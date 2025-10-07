from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import openai
import os
from typing import List, Optional
import uuid
import aiofiles
from datetime import datetime, timedelta
import stripe
from decouple import config

from database import get_db, engine, Base
from models import User, Transcription, APIKey
from subscription_models import Subscription, Usage
from schemas import (
    UserCreate, UserResponse, TranscriptionResponse, 
    TranscriptionCreate, APIKeyCreate, APIKeyResponse,
    SubscriptionCreate, SubscriptionResponse
)
from auth import create_access_token, verify_token, get_password_hash, verify_password
from payment import payment_service

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Voice Transcription SaaS",
    description="A powerful AI-powered voice transcription service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
JWT_SECRET_KEY = config("JWT_SECRET_KEY", default="your-secret-key-here")

openai.api_key = OPENAI_API_KEY
stripe.api_key = STRIPE_SECRET_KEY

security = HTTPBearer()

# Upload directory
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "AI Voice Transcription SaaS API", "version": "1.0.0"}

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        created_at=db_user.created_at
    )

@app.post("/auth/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # Verify token and get user
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Check file type
    if not file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file"
        )
    
    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'wav'
    file_path = f"{UPLOAD_DIR}/{file_id}.{file_extension}"
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    try:
        # Transcribe using OpenAI Whisper
        with open(file_path, 'rb') as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        
        # Save transcription to database
        db_transcription = Transcription(
            user_id=user.id,
            filename=file.filename,
            transcription_text=transcript.text,
            file_size=len(content),
            duration=0  # We could extract this from audio metadata
        )
        db.add(db_transcription)
        db.commit()
        db.refresh(db_transcription)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return TranscriptionResponse(
            id=db_transcription.id,
            filename=db_transcription.filename,
            transcription_text=db_transcription.transcription_text,
            file_size=db_transcription.file_size,
            duration=db_transcription.duration,
            created_at=db_transcription.created_at
        )
    
    except Exception as e:
        # Clean up uploaded file in case of error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )

@app.get("/transcriptions", response_model=List[TranscriptionResponse])
async def get_transcriptions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    transcriptions = db.query(Transcription).filter(
        Transcription.user_id == user.id
    ).offset(skip).limit(limit).all()
    
    return [
        TranscriptionResponse(
            id=t.id,
            filename=t.filename,
            transcription_text=t.transcription_text,
            file_size=t.file_size,
            duration=t.duration,
            created_at=t.created_at
        )
        for t in transcriptions
    ]

@app.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    api_key_data: APIKeyCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Generate API key
    api_key = f"tsk_{uuid.uuid4().hex}"
    
    db_api_key = APIKey(
        user_id=user.id,
        key=api_key,
        name=api_key_data.name
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return APIKeyResponse(
        id=db_api_key.id,
        name=db_api_key.name,
        key=api_key,
        created_at=db_api_key.created_at
    )

@app.get("/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    api_keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
    
    return [
        APIKeyResponse(
            id=key.id,
            name=key.name,
            key=key.key[:8] + "..." + key.key[-4:],  # Mask the key
            created_at=key.created_at
        )
        for key in api_keys
    ]

@app.post("/subscriptions/create-checkout", response_model=dict)
async def create_checkout_session(
    subscription_data: SubscriptionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Check if user already has a customer ID
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    
    if not subscription or not subscription.stripe_customer_id:
        # Create Stripe customer
        customer_id = await payment_service.create_customer(user)
        
        if not subscription:
            # Create subscription record
            subscription = Subscription(
                user_id=user.id,
                stripe_customer_id=customer_id,
                plan_name=subscription_data.plan_name,
                status="incomplete"
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
        else:
            subscription.stripe_customer_id = customer_id
            db.commit()
    
    # Create checkout session
    success_url = "http://localhost:3000/dashboard?success=true"
    cancel_url = "http://localhost:3000/dashboard?canceled=true"
    
    checkout_url = await payment_service.create_checkout_session(
        subscription.stripe_customer_id,
        subscription_data.price_id,
        success_url,
        cancel_url
    )
    
    return {"checkout_url": checkout_url}

@app.get("/subscriptions/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    
    if not subscription:
        # Create default free subscription
        subscription = Subscription(
            user_id=user.id,
            plan_name="starter",
            status="active",
            monthly_transcription_limit=60,
            monthly_transcription_used=0
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return SubscriptionResponse(
        id=subscription.id,
        plan_name=subscription.plan_name,
        status=subscription.status,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end,
        monthly_transcription_limit=subscription.monthly_transcription_limit,
        monthly_transcription_used=subscription.monthly_transcription_used,
        created_at=subscription.created_at
    )

@app.post("/subscriptions/cancel")
async def cancel_subscription(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    
    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    # Cancel subscription in Stripe
    result = await payment_service.cancel_subscription(subscription.stripe_subscription_id)
    
    # Update local subscription
    subscription.status = "canceled"
    subscription.cancel_at_period_end = True
    db.commit()
    
    return {"message": "Subscription canceled successfully", "status": result["status"]}

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event_data = await payment_service.handle_webhook(payload.decode(), sig_header)
        
        # Handle different event types
        if event_data["type"] == "subscription_created":
            subscription_data = event_data["subscription"]
            # Update local subscription record
            # Implementation depends on your needs
            
        elif event_data["type"] == "subscription_updated":
            subscription_data = event_data["subscription"]
            # Update local subscription record
            
        elif event_data["type"] == "subscription_deleted":
            subscription_data = event_data["subscription"]
            # Mark subscription as canceled
            
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)