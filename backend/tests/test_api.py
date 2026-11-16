from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["model_loaded"] is True


def test_model_metrics():
    r = client.get("/api/model")
    assert r.status_code == 200
    assert r.json()["best_model"] in r.json()["models"]


def test_kyc_scam_is_fraud():
    r = client.post("/api/analyze", json={
        "message": "Dear Customer, your SBI account will be BLOCKED today due to pending KYC. "
                   "Update immediately: http://bit.ly/sbi-kyc-upd or call 9876543210.",
        "sender": "+44 7700 900123",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] == "fraud"
    assert body["ml"]["label"] == "fraud"
    assert "http://bit.ly/sbi-kyc-upd" in body["links"]
    assert any(f["id"] == "reported-in-msg" for f in body["flags"])


def test_casual_message_is_safe():
    r = client.post("/api/analyze", json={"message": "Are we still meeting at 6 for dinner?"})
    assert r.status_code == 200
    assert r.json()["verdict"] == "safe"


def test_genuine_bank_otp_not_fraud():
    r = client.post("/api/analyze", json={
        "message": "Your OTP for transaction of Rs 2,500 at Myntra is 739201. "
                   "Do not share it with anyone. -HDFC Bank"})
    assert r.status_code == 200
    assert r.json()["verdict"] != "fraud"


def test_validation_rejects_short_message():
    assert client.post("/api/analyze", json={"message": "hi"}).status_code == 422


def test_validation_rejects_bad_sender():
    r = client.post("/api/analyze", json={"message": "hello there friend", "sender": "abc<script>"})
    assert r.status_code == 422
