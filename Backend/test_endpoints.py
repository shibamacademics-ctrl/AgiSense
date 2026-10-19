"""
Quick smoke test for all three endpoints using FastAPI's TestClient
(runs in-process, no need for a live server -- useful in sandboxed
environments where background processes don't persist).
"""

import sys
import pathlib
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("1. Health check")
print("=" * 60)
r = client.get("/health")
print(r.status_code, r.json())

print("\n" + "=" * 60)
print("2. POST /recommend-crop")
print("=" * 60)
crop_payload = {
    "N": 90, "P": 42, "K": 43,
    "temperature": 20.88, "humidity": 82.0,
    "ph": 6.5, "rainfall": 202.9
}
r = client.post("/recommend-crop", json=crop_payload)
print(r.status_code)
print(r.json())

print("\n" + "=" * 60)
print("3. POST /predict-yield")
print("=" * 60)
yield_payload = {
    "Area": "India",
    "Item": "Rice, paddy",
    "Year": 2013,
    "average_rain_fall_mm_per_year": 1083.0,
    "pesticides_tonnes": 500.0,
    "avg_temp": 26.5
}
r = client.post("/predict-yield", json=yield_payload)
print(r.status_code)
print(r.json())

print("\n" + "=" * 60)
print("4. POST /detect-disease")
print("=" * 60)
image_dir = pathlib.Path(__file__).resolve().parents[1] / "data" / "PlantVillage" / "Tomato_Late_blight"
# Pick the first image file in the directory for testing
image_path = next(image_dir.iterdir())
with open(image_path, "rb") as f:
    files = {"file": ("leaf.jpg", f, "image/jpeg")}
    r = client.post("/detect-disease", files=files)
print(r.status_code)
print(r.json())

print("\n" + "=" * 60)
print("5. Error handling: bad crop input (out of range)")
print("=" * 60)
bad_payload = {**crop_payload, "ph": 20}  # ph max is 14
r = client.post("/recommend-crop", json=bad_payload)
print(r.status_code)
print(r.json())

print("\n" + "=" * 60)
print("6. Error handling: wrong file type for disease detection")
print("=" * 60)
r = client.post("/detect-disease", files={"file": ("test.txt", b"not an image", "text/plain")})
print(r.status_code)
print(r.json())
