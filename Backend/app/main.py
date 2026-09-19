#!/usr/bin/env python
# coding: utf-8

# In[8]:


from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    YieldPredictionRequest,
    YieldPredictionResponse,
    DiseaseDetectionResponse
)

from app import model_loader
app = FastAPI(
    title="AI-Driven Crop Detection and Management System API",
    description="Crop recommendation, disease detection, and yield prediction endpoints.",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health_check():
    return {"STATUS": "OK!"}
@app.post(
    "/recommend-crop",
    response_model=CropRecommendationResponse
)
def recommend_crop(request: CropRecommendationRequest):
    try:
        result = model_loader.predict_crop(request.model_dump())
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Crop recommendation failed: {str(e)}"
        )
@app.post(
    "/predict-yield",
    response_model=YieldPredictionResponse
)
def predict_yield(request: YieldPredictionRequest):
    try:
        result = model_loader.predict_yield(request.model_dump())
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Yield prediction failed: {str(e)}"
        )
@app.post(
    "/detect-disease",
    response_model=DiseaseDetectionResponse
)
async def detect_disease(file: UploadFile = File(...)):

    allowed_types = {
        "image/jpeg",
        "image/jpg",
        "image/png"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. "
                   "Upload a JPEG or PNG image."
        )

    try:
        image_bytes = await file.read()

        result = model_loader.predict_disease(image_bytes)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Disease detection failed: {str(e)}"
        )

