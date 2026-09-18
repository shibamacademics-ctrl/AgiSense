#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pydantic import BaseModel,Field
from typing import List


# In[2]:


class CropRecommendationRequest(BaseModel):
    N: float = Field(..., ge=0, le=200, description="Nitrogen content in soil")
    P: float = Field(..., ge=0, le=200, description="Phosphorus content in soil")
    K: float = Field(..., ge=0, le=250, description="Potassium content in soil")
    temperature: float = Field(..., ge=-10, le=60, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity in %")
    ph: float = Field(..., ge=0, le=14, description="Soil pH")
    rainfall: float = Field(..., ge=0, le=500, description="Rainfall in mm")
    class Config:
        json_schema_extra = {
            "example" : {
                "N" : 90, "P" : 42, "K" : 43,
                "temperature": 20.88, "humidity": 82.0,
                "ph": 6.5, "rainfall": 202.9
            }
        }
class CropRecommendationResponse(BaseModel):
    recommended_crop: str
    confidence: float
    top_3_alternatives: List[dict]


# In[3]:


class YieldPredictionRequest(BaseModel):
    Area: str = Field(..., description="Country/region name")
    Item: str = Field(..., description="Crop name, e.g. 'Maize', 'Wheat'")
    Year: int = Field(..., ge=1960, le=2030)
    average_rain_fall_mm_per_year: float = Field(..., ge=0)
    pesticides_tonnes: float = Field(..., ge=0)
    avg_temp: float = Field(..., ge=-30, le=50)
    class Config:
        json_schema_extra = {
            "example": {
                "Area": "India",
                "Item": "Rice, paddy",
                "Year": 2013,
                "average_rain_fall_mm_per_year": 1083.0,
                "pesticides_tonnes": 500.0,
                "avg_temp": 26.5
            }
        }
class YieldPredictionResponse(BaseModel):
    predicted_yield_hg_per_ha: float
    predicted_yield_tonnes_per_ha: float


# In[4]:


class DiseaseDetectionResponse(BaseModel):
    predicted_disease: str
    confidence: float
    treatment_suggestion: str
    top_3_alternatives: List[dict]
    low_confidence_warning: bool

