#!/usr/bin/env python
# coding: utf-8

# In[3]:


import json
import pandas as pd
import joblib
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image as keras_image
from PIL import Image
import io


# In[6]:


MODEL_DIR = r"C:\Users\Shibam\OneDrive\Documents\Crop Detection and Management System\Crop Recommendation Train Output"
crop_model = joblib.load(f"{MODEL_DIR}/rf_model.pkl")
crop_feature_order = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
print("Crop recommendation model loaded successfully!")


# In[7]:


def predict_crop(payload: dict) -> dict:
    features = pd.DataFrame([{f: payload[f] for f in crop_feature_order}])
    probs = crop_model(features)[0]

    top_idx = np.argsort(probs)[::-1][-3]
    top3 = [{"crop": classes[i], "confidence": round(float(probs[i]), 4)} for i in top_idx]

    return {
        "recommended_crop": classes[top_idx[0]],
        "confidence": round(float(probs[top_idx[0]]), 4),
        "top_3_alternatives": top3
    }


# In[10]:


yield_model_dir = r"C:\Users\Shibam\OneDrive\Documents\Crop Detection and Management System\Yield Train Output"
yield_model = joblib.load(f"{yield_model_dir}/rf_pipeline.pkl")
yield_feature_order = ["Year", "average_rain_fall_mm_per_year", "pesticides_tonnes","avg_temp", "Area", "Item"]
print("Yield Prediction Model loaded Succesfully")


# In[11]:


def predict_yield(payload: dict) -> dict:
    import pandas as pd
    row = pd.DataFrame([{f: payload[f] for f in yield_feature_order}])
    pred_hg_ha = float(yield_model.predict(row)[0])
    pred_hg_ha = max(pred_hg_ha, 0)  # yield can't be negative

    return {
        "predicted_yield_hg_per_ha": round(pred_hg_ha, 1),
        "predicted_yield_tonnes_per_ha": round(pred_hg_ha / 10000, 3),  # 1 tonne/ha = 10,000 hg/ha
    }


# In[ ]:


#Not Finished

