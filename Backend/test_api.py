from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app import main


client = TestClient(main.app)


CROP_INPUT = {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.88,
    "humidity": 82,
    "ph": 6.5,
    "rainfall": 202.9,
}


def test_health_contract_is_unchanged():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"STATUS": "OK!"}


def test_crop_recommendation_keeps_response_and_records_history(monkeypatch):
    expected = {
        "recommended_crop": "rice",
        "confidence": 0.91,
        "top_3_alternatives": [{"crop": "rice", "confidence": 0.91}],
    }
    saved = {}
    monkeypatch.setattr(main.model_loader, "predict_crop", lambda payload: expected)
    monkeypatch.setattr(main, "save_query", lambda **kwargs: saved.update(kwargs))

    response = client.post("/recommend-crop", json=CROP_INPUT, headers={"X-Farmer-ID": "farmer-123"})

    assert response.status_code == 200
    assert response.json() == expected
    assert saved["farmer_id"] == "farmer-123"
    assert saved["query_type"] == "crop_recommendation"
    assert saved["request_payload"] == CROP_INPUT
    assert saved["response_payload"] == expected


def test_invalid_crop_input_is_rejected_before_model_call(monkeypatch):
    called = False

    def fail_if_called(_):
        nonlocal called
        called = True
        raise AssertionError("model should not run for invalid input")

    monkeypatch.setattr(main.model_loader, "predict_crop", fail_if_called)
    invalid = {**CROP_INPUT, "humidity": 101}

    response = client.post("/recommend-crop", json=invalid)

    assert response.status_code == 422
    assert called is False


def test_history_endpoint_returns_saved_records(monkeypatch):
    created_at = datetime.now(timezone.utc)
    record = type(
        "Record",
        (),
        {
            "id": 1,
            "farmer_id": "farmer-123",
            "query_type": "crop_recommendation",
            "request_payload": CROP_INPUT,
            "response_payload": {"recommended_crop": "rice", "confidence": 0.91, "top_3_alternatives": []},
            "created_at": created_at,
        },
    )()
    monkeypatch.setattr(main, "list_queries", lambda **kwargs: [record])

    response = client.get("/farmer-queries?farmer_id=farmer-123&limit=10")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["items"][0]["farmer_id"] == "farmer-123"
    assert body["items"][0]["query_type"] == "crop_recommendation"


def test_disease_rejects_non_image_without_running_model(monkeypatch):
    monkeypatch.setattr(main.model_loader, "predict_disease", lambda _: (_ for _ in ()).throw(AssertionError()))

    response = client.post("/detect-disease", files={"file": ("notes.txt", b"not an image", "text/plain")})

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
