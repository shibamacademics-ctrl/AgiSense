import io
import json
import os
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from PIL import Image

BASE_DIR = Path(__file__).resolve().parents[2]
CROP_MODEL_DIR = Path(os.getenv("CROP_MODEL_DIR", BASE_DIR / "Crop Recommendation Train Output"))
YIELD_MODEL_DIR = Path(os.getenv("YIELD_MODEL_DIR", BASE_DIR / "Yield Train Output"))
DISEASE_MODEL_DIR = Path(os.getenv("DISEASE_MODEL_DIR", BASE_DIR / "Disease Detection Output"))

CROP_FEATURE_ORDER = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
YIELD_FEATURE_ORDER = ["Year", "average_rain_fall_mm_per_year", "pesticides_tonnes", "avg_temp", "Area", "Item"]


@lru_cache(maxsize=1)
def get_crop_model():
    return joblib.load(CROP_MODEL_DIR / "rf_model.pkl")


@lru_cache(maxsize=1)
def get_yield_model():
    return joblib.load(YIELD_MODEL_DIR / "rf_pipeline.pkl")


@lru_cache(maxsize=1)
def get_disease_assets():
    import tensorflow as tf
    from tensorflow.keras.preprocessing import image as keras_image

    with (DISEASE_MODEL_DIR / "disease_detection_classes.json").open() as f:
        classes = json.load(f)
    with (DISEASE_MODEL_DIR / "disease_detection_config.json").open() as f:
        config = json.load(f)
    model = tf.keras.models.load_model(
        DISEASE_MODEL_DIR / f"disease_detection_{config['model_name']}_phase1.keras"
    )
    return model, classes, config, keras_image


TREATMENT_SUGGESTIONS = {
    "Pepper__bell___Bacterial_spot": "Apply copper-based bactericide; avoid overhead watering; remove infected leaves.",
    "Pepper__bell___healthy": "No action needed. Maintain regular watering and monitoring.",
    "Potato___Early_blight": "Apply fungicide (chlorothalonil/mancozeb); rotate crops; remove infected foliage.",
    "Potato___Late_blight": "Apply fungicide immediately; destroy infected plants; avoid overhead irrigation.",
    "Potato___healthy": "No action needed. Maintain regular watering and monitoring.",
    "Tomato_Bacterial_spot": "Apply copper-based spray; avoid working with wet plants; remove debris.",
    "Tomato_Early_blight": "Apply fungicide; mulch around base; remove lower infected leaves.",
    "Tomato_Late_blight": "Apply fungicide immediately; this spreads fast -- isolate affected plants.",
    "Tomato_Leaf_Mold": "Improve air circulation; reduce humidity; apply fungicide if severe.",
    "Tomato_Septoria_leaf_spot": "Remove infected leaves; apply fungicide; avoid overhead watering.",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Apply miticide or insecticidal soap; increase humidity.",
    "Tomato__Target_Spot": "Apply fungicide; improve air circulation; remove infected debris.",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Remove infected plants; control whitefly population (vector); no cure once infected.",
    "Tomato__Tomato_mosaic_virus": "Remove and destroy infected plants; disinfect tools; no cure once infected.",
    "Tomato_healthy": "No action needed. Maintain regular watering and monitoring.",
}


def predict_crop(payload: dict) -> dict:
    crop_model = get_crop_model()
    features = pd.DataFrame([{feature: payload[feature] for feature in CROP_FEATURE_ORDER}])
    probs = crop_model.predict_proba(features)[0]
    classes = crop_model.classes_
    top_indices = np.argsort(probs)[::-1][:3]
    top3 = [{"crop": classes[i], "confidence": round(float(probs[i]), 4)} for i in top_indices]
    return {"recommended_crop": classes[top_indices[0]], "confidence": round(float(probs[top_indices[0]]), 4), "top_3_alternatives": top3}


def predict_yield(payload: dict) -> dict:
    yield_model = get_yield_model()
    row = pd.DataFrame([{feature: payload[feature] for feature in YIELD_FEATURE_ORDER}])
    pred_hg_ha = max(float(yield_model.predict(row)[0]), 0)
    return {"predicted_yield_hg_per_ha": round(pred_hg_ha, 1), "predicted_yield_tonnes_per_ha": round(pred_hg_ha / 10000, 3)}


def predict_disease(image_bytes: bytes) -> dict:
    disease_model, disease_classes, disease_config, keras_image = get_disease_assets()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((disease_config["img_size"], disease_config["img_size"]))
    arr = keras_image.img_to_array(img) / 255.0
    probs = disease_model.predict(np.expand_dims(arr, axis=0), verbose=0)[0]
    top_indices = np.argsort(probs)[::-1][:3]
    top3 = [{"disease": disease_classes[i], "confidence": round(float(probs[i]), 4)} for i in top_indices]
    top_class = top3[0]["disease"]
    top_confidence = top3[0]["confidence"]
    return {
        "predicted_disease": top_class,
        "confidence": top_confidence,
        "treatment_suggestion": TREATMENT_SUGGESTIONS.get(top_class, "No suggestion available."),
        "top_3_alternatives": top3,
        "low_confidence_warning": top_confidence < 0.6,
    }
