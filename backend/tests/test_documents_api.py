"""
Integration Tests for Document Ingestion API and State Tracking.
"""

import io
import time
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_upload_document_success():
    """Verify document upload endpoint returns 202 Accepted and initializes metadata."""
    content = b"Aegis Knowledge Intelligence Document.\nSection 1: Data Verification.\nClaims must be grounded in facts."
    files = {"file": ("test_doc.txt", io.BytesIO(content), "text/plain")}

    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 202
    data = response.json()

    assert "document_id" in data
    assert data["filename"] == "test_doc.txt"
    assert data["file_type"] == "txt"
    assert data["size_bytes"] == len(content)
    assert data["status"] in ["UPLOADED", "PROCESSING", "COMPLETED"]

    doc_id = data["document_id"]

    # Verify listing includes the new document
    list_resp = client.get("/api/v1/documents")
    assert list_resp.status_code == 200
    docs = list_resp.json()
    assert any(d["document_id"] == doc_id for d in docs)

    # Verify document detail endpoint
    get_resp = client.get(f"/api/v1/documents/{doc_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["document_id"] == doc_id


def test_upload_document_invalid_extension():
    """Verify upload rejects unsupported file extensions."""
    content = b"executable binary data"
    files = {"file": ("malicious.exe", io.BytesIO(content), "application/octet-stream")}

    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]


def test_upload_empty_document():
    """Verify upload rejects empty files."""
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}

    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    assert "File is empty" in response.json()["detail"]


def test_delete_document():
    """Verify deleting a document removes it from records."""
    content = b"Temporary content to be deleted."
    files = {"file": ("temp.txt", io.BytesIO(content), "text/plain")}

    upload_resp = client.post("/api/v1/documents/upload", files=files)
    doc_id = upload_resp.json()["document_id"]

    del_resp = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_resp.status_code == 204

    # Confirm 404 on subsequent get
    get_resp = client.get(f"/api/v1/documents/{doc_id}")
    assert get_resp.status_code == 404
