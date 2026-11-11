#!/usr/bin/env python
# coding: utf-8
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app import model_loader
from app.auth import create_access_token, decode_access_token, hash_password, verify_password
from app.auth_schemas import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.database import create_user, get_user_by_email, get_user_by_id, init_db, list_queries, save_query
from app.history_schemas import FarmerQueryHistoryResponse
from app.schemas import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    DiseaseDetectionResponse,
    YieldPredictionRequest,
    YieldPredictionResponse,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        init_db()
    except Exception:
        logger.exception("PostgreSQL initialization failed; history persistence is disabled")
    yield


app = FastAPI(
    title="AI-Driven Crop Detection and Management System API",
    description="Crop recommendation, disease detection, yield prediction, and farmer query history endpoints.",
    version="1.1",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000,http://localhost:5173,https://agrisense-ruddy-three.vercel.app").split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def record_query(*, farmer_id: Optional[str], query_type: str, request_payload: dict, response_payload: dict) -> None:
    """Persist history on a best-effort basis so prediction behavior is unchanged."""
    try:
        save_query(
            farmer_id=farmer_id,
            query_type=query_type,
            request_payload=request_payload,
            response_payload=response_payload,
        )
    except Exception:
        logger.exception("Could not persist %s query", query_type)


def user_response(user) -> UserResponse:
    return UserResponse(id=user.id, name=user.name, email=user.email, created_at=user.created_at)


def current_user(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Please sign in first")
    payload = decode_access_token(authorization.split(" ", 1)[1])
    user = get_user_by_id(int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User account was not found")
    return user


@app.post("/auth/register", response_model=AuthResponse, status_code=201)
def register(request: RegisterRequest):
    if get_user_by_email(request.email) is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    try:
        user = create_user(name=request.name, email=request.email, password_hash=hash_password(request.password))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    if user is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return AuthResponse(access_token=create_access_token(user.id, user.email), user=user_response(user))


@app.post("/auth/login", response_model=AuthResponse)
def login(request: LoginRequest):
    user = get_user_by_email(request.email)
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthResponse(access_token=create_access_token(user.id, user.email), user=user_response(user))


@app.get("/auth/me", response_model=UserResponse)
def me(user=Depends(current_user)):
    return user_response(user)


@app.get("/health")
def health_check():
    return {"STATUS": "OK!"}


@app.post("/recommend-crop", response_model=CropRecommendationResponse)
def recommend_crop(request: CropRecommendationRequest, x_farmer_id: Optional[str] = Header(default=None)):
    try:
        result = model_loader.predict_crop(request.model_dump())
        record_query(farmer_id=x_farmer_id, query_type="crop_recommendation", request_payload=request.model_dump(), response_payload=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crop recommendation failed: {str(e)}") from e


@app.post("/predict-yield", response_model=YieldPredictionResponse)
def predict_yield(request: YieldPredictionRequest, x_farmer_id: Optional[str] = Header(default=None)):
    try:
        result = model_loader.predict_yield(request.model_dump())
        record_query(farmer_id=x_farmer_id, query_type="yield_prediction", request_payload=request.model_dump(), response_payload=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yield prediction failed: {str(e)}") from e


@app.post("/detect-disease", response_model=DiseaseDetectionResponse)
async def detect_disease(file: UploadFile = File(...), x_farmer_id: Optional[str] = Header(default=None)):
    allowed_types = {"image/jpeg", "image/jpg", "image/png"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{file.content_type}'. Upload a JPEG or PNG image.")
    try:
        image_bytes = await file.read()
        logger.info("Disease request received: filename=%s bytes=%s", file.filename, len(image_bytes))
        started_at = time.perf_counter()
        result = model_loader.predict_disease(image_bytes)
        logger.info("Disease inference completed in %.2f seconds", time.perf_counter() - started_at)
        record_query(
            farmer_id=x_farmer_id,
            query_type="disease_detection",
            request_payload={"filename": file.filename, "content_type": file.content_type},
            response_payload=result,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disease detection failed: {str(e)}") from e


@app.get("/farmer-queries", response_model=FarmerQueryHistoryResponse)
def farmer_queries(farmer_id: Optional[str] = Query(default=None), limit: int = Query(default=50, ge=1, le=100)):
    records = list_queries(farmer_id=farmer_id, limit=limit)
    return {"items": records, "count": len(records)}
