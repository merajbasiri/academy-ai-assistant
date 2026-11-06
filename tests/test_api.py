from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dashboard_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "Academy AI Assistant" in response.text


def test_dashboard_assets_are_served():
    assert client.get("/assets/styles.css").status_code == 200
    assert client.get("/assets/app.js").status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_student_index():
    response = client.get("/students")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_summary():
    response = client.get("/summary")
    assert response.status_code == 200
    assert response.json()["total_outstanding"] == 10_000_000


def test_student_endpoint():
    response = client.get("/students/ST001")
    assert response.status_code == 200
    assert response.json()["student_id"] == "ST001"


def test_student_endpoint_not_found():
    assert client.get("/students/ST999").status_code == 404


def test_balance_endpoint():
    response = client.get("/students/ST001/balance")
    assert response.status_code == 200
    assert response.json()["balance"] == 4_500_000


def test_chat_rejects_too_short_message():
    assert client.post("/chat", json={"message": "x"}).status_code == 422


def test_chat_without_api_key_returns_clear_status(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/chat", json={"message": "Tuition for ST001?"})
    assert response.status_code == 503
    assert response.json()["detail"].startswith("OPENAI_API_KEY")


def test_config_reports_only_availability(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    response = client.get("/config")
    assert response.json() == {"chat_enabled": True}
    assert "test-secret" not in response.text