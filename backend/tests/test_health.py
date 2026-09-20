from fastapi.testclient import TestClient
from backend.app.main import app
client = TestClient(app)
def test_root_health():
    assert client.get('/health').status_code == 200
