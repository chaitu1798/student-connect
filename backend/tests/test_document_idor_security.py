import os
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.student import Student
from app.models.internship import Internship
from app.models.document import StudentDocument, InternshipCertificate
from app.models.permissions import PublicProfilePermission
from app.config import settings

client = TestClient(app)

@pytest.fixture(scope="module")
def admin_token():
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "vignan123"})
    if res.status_code != 200:
        res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    if res.status_code != 200:
        res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "SecurePassword2026!"})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def client_token():
    res = client.post("/api/v1/auth/login", json={"username": "client", "password": "Client123!"})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def setup_test_documents(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Create a student with private profile
    client.post("/api/v1/students", headers=headers, json={
        "roll_no": "IDOR_STUDENT_01",
        "full_name": "IDOR Test Student",
        "branch": "CSE"
    })
    
    # Upload Aadhaar document as admin
    dummy_img = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00"
    files = {"file": ("aadhaar_card.jpg", dummy_img, "image/jpeg")}
    up_res = client.post("/api/v1/documents/student/IDOR_STUDENT_01/upload", headers=headers, data={"doc_type": "aadhaar"}, files=files)
    assert up_res.status_code == 200
    aadhaar_path = up_res.json()["path"]

    # Upload private other document
    files_other = {"file": ("private_notes.pdf", b"%PDF-1.4 dummy", "application/pdf")}
    other_res = client.post("/api/v1/documents/student/IDOR_STUDENT_01/upload", headers=headers, data={"doc_type": "other"}, files=files_other)
    assert other_res.status_code == 200
    private_doc_path = other_res.json()["path"]

    # Upload certificate for internship
    i_res = client.post("/api/v1/internships", headers=headers, json={
        "roll_no": "IDOR_STUDENT_01",
        "full_name": "IDOR Test Student",
        "organization_name": "SecureCorp"
    })
    assert i_res.status_code == 201
    i_id = i_res.json()["id"]

    files_cert = {"file": ("cert.pdf", b"%PDF-1.4 cert", "application/pdf")}
    cert_res = client.post(f"/api/v1/documents/internship/{i_id}/certificate", headers=headers, files=files_cert)
    assert cert_res.status_code == 200
    cert_path = cert_res.json()["path"]

    # Make certificate authorized by approving public internships for this student
    client.put(
        "/api/v1/admin/permissions/IDOR_STUDENT_01",
        headers=headers,
        json={
            "is_public_approved": True,
            "student_consent_given": True,
            "publish_internships": True,
            "publish_cgpa": False,
            "publish_gender": False
        }
    )

    return {
        "aadhaar_path": aadhaar_path,
        "private_doc_path": private_doc_path,
        "cert_path": cert_path,
    }

# 1. Admin downloading an authorized document (including Aadhaar)
def test_1_admin_can_download_any_document(admin_token, setup_test_documents):
    headers = {"Authorization": f"Bearer {admin_token}"}
    aadhaar_path = setup_test_documents["aadhaar_path"]
    res = client.get(f"/api/v1/documents/download?path={aadhaar_path}", headers=headers)
    assert res.status_code == 200

# 2. Client downloading an authorized certificate
def test_2_client_can_download_authorized_certificate(client_token, setup_test_documents):
    headers = {"Authorization": f"Bearer {client_token}"}
    cert_path = setup_test_documents["cert_path"]
    res = client.get(f"/api/v1/documents/download?path={cert_path}", headers=headers)
    assert res.status_code == 200

# 3. Client attempting to download an Aadhaar document -> HTTP 403 Forbidden
def test_3_client_cannot_download_aadhaar(client_token, setup_test_documents):
    headers = {"Authorization": f"Bearer {client_token}"}
    aadhaar_path = setup_test_documents["aadhaar_path"]
    res = client.get(f"/api/v1/documents/download?path={aadhaar_path}", headers=headers)
    assert res.status_code == 403
    assert "Aadhaar" in res.json()["detail"]

# 4. Client attempting to download another student's private document -> HTTP 403 Forbidden
def test_4_client_cannot_download_private_student_document(client_token, setup_test_documents):
    headers = {"Authorization": f"Bearer {client_token}"}
    private_path = setup_test_documents["private_doc_path"]
    res = client.get(f"/api/v1/documents/download?path={private_path}", headers=headers)
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]

# 5. Unauthenticated download attempts -> HTTP 401 Unauthorized
def test_5_unauthenticated_download_rejected(setup_test_documents):
    cert_path = setup_test_documents["cert_path"]
    client.cookies.clear()
    res = client.get(f"/api/v1/documents/download?path={cert_path}")
    assert res.status_code == 401

# 6. Invalid or manipulated document paths -> HTTP 400 or 403
def test_6_path_traversal_manipulation_rejected(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Path traversal attack
    res1 = client.get("/api/v1/documents/download?path=../../etc/passwd", headers=headers)
    assert res1.status_code in [400, 403]

    # Non-existent file in upload dir
    res2 = client.get("/api/v1/documents/download?path=documents/nonexistent_file_9999.pdf", headers=headers)
    assert res2.status_code == 404

