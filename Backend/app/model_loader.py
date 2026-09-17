import json
import pandas as pd
import joblib
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image as keras_image
from PIL import Image
import io
MODEL_DIR = r"C:\Users\Shibam\OneDrive\Documents\Crop Detection and Management System\Crop Recommendation Train Output"
crop_model = joblib.load(f"{MODEL_DIR}/rf_model.pkl")
crop_feature_order = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
print("Crop recommendation model loaded successfully!")

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


yield_model_dir = r"C:\Users\Shibam\OneDrive\Documents\Crop Detection and Management System\Yield Train Output"
yield_model = joblib.load(f"{yield_model_dir}/rf_pipeline.pkl")
yield_feature_order = ["Year", "average_rain_fall_mm_per_year", "pesticides_tonnes","avg_temp", "Area", "Item"]
print("Yield Prediction Model loaded Succesfully")

def predict_yield(payload: dict) -> dict:
    import pandas as pd
    row = pd.DataFrame([{f: payload[f] for f in yield_feature_order}])
    pred_hg_ha = float(yield_model.predict(row)[0])
    pred_hg_ha = max(pred_hg_ha, 0)  # yield can't be negative

    return {
        "predicted_yield_hg_per_ha": round(pred_hg_ha, 1),
        "predicted_yield_tonnes_per_ha": round(pred_hg_ha / 10000, 3),  # 1 tonne/ha = 10,000 hg/ha
    }

disease_model_dir = r"C:\Users\Shibam\OneDrive\Documents\Crop Detection and Management System\Disease Detection Output"
with open(f"{disease_model_dir}/disease_detection_classes.json") as f:
    disease_classes = json.load(f)
with open(f"{disease_model_dir}/disease_detection_config.json") as f:
    disease_config = json.load(f)

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
    "Tomato_healthy": "No action needed. Maintain regular watering and monitoring."   
}
disease_model_name = disease_config["model_name"]
disease_img_size = disease_config["img_size"]
disease_model = tf.keras.models.load_model(
    f"{disease_model_dir}/disease_detection_{disease_model_name}_phase1.keras"
)

def predict_disease(image_bytes : bytes) -> dict:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((disease_img_size,disease_img_size))
    arr = keras_image.img_to_array(img) / 255.0
    input_arr = np.expand_dims(arr, axis=0)
    probs = disease_model.predict(input_arr,verbose=0)[0]
    top_indices = np.argsort(probs)[::-1][:3]
    top3 = [{"disease": disease_classes[i], "confidence": round(float(probs[i]), 4)}
            for i in top_indices]
    top_class = top3[0]["disease"]
    top_confidence = top3[0]["confidence"]

    return {
        "predicted_disease": top_class,
        "confidence": top_confidence,
        "treatment_suggestion": TREATMENT_SUGGESTIONS.get(top_class, "No suggestion available."),
        "top_3_alternatives": top3,
        "low_confidence_warning": top_confidence < 0.6,
    }

