#!/usr/bin/env python
# coding: utf-8
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app import model_loader
from app.database import init_db, list_queries, save_query
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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
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
        result = model_loader.predict_disease(image_bytes)
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
