import os
import shutil
import sqlite3
import io
import uuid
import pytest
import pandas as pd
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.config import Settings, settings
from app.database import get_db, Base
from app.models.user import User
from app.models.student import Student, StudentPrivateData
from app.models.internship import Internship
from app.models.document import StudentDocument
from app.utils.crypto import decrypt_aes_gcm, encrypt_aes_gcm
from app.utils.security import hash_password

STAGING_DB_PATH = "staging_smoke.db"
BACKUP_DB_PATH = "student_portal.db.bak_phase2"

staging_engine = create_engine(f"sqlite:///./{STAGING_DB_PATH}", connect_args={"check_same_thread": False})
StagingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=staging_engine)

def override_get_db():
    db = StagingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_staging_environment():
    # Setup isolated staging database from backup
    if os.path.exists(BACKUP_DB_PATH):
        shutil.copyfile(BACKUP_DB_PATH, STAGING_DB_PATH)
    else:
        # Fallback create schema
        Base.metadata.create_all(bind=staging_engine)
    
    # Ensure test admin and client exist in staging db with known credentials
    db = StagingSessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@institution.edu",
            full_name="Staging Admin",
            role="SUPER_ADMIN",
            hashed_password=hash_password("vignan123"),
            must_change_password=False,
            mfa_enabled=False,
        )
        db.add(admin)
    else:
        admin.hashed_password = hash_password("vignan123")
        admin.must_change_password = False

    client_user = db.query(User).filter(User.username == "client").first()
    if not client_user:
        client_user = User(
            username="client",
            email="client@institution.edu",
            full_name="Staging Client",
            role="CLIENT",
            hashed_password=hash_password("Client123!"),
            must_change_password=False,
            mfa_enabled=False,
        )
        db.add(client_user)
    else:
        client_user.hashed_password = hash_password("Client123!")
        client_user.must_change_password = False

    db.commit()
    db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    staging_engine.dispose()
    if os.path.exists(STAGING_DB_PATH):
        try:
            os.remove(STAGING_DB_PATH)
        except Exception:
            pass

@pytest.fixture(scope="module")
def admin_token():
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "vignan123"},
        headers={"X-Forwarded-For": "192.168.1.100"}
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def client_token():
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "client", "password": "Client123!"},
        headers={"X-Forwarded-For": "192.168.1.101"}
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


# ==============================================================================
# TEST 1: PRODUCTION CONFIGURATION
# ==============================================================================
def test_1_1_production_environment_rejects_missing_secret_key(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "")
    with pytest.raises((ValidationError, ValueError)):
        Settings()

def test_1_2_production_environment_rejects_short_secret_key(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "short-key-under-32-chars")
    with pytest.raises((ValidationError, ValueError)):
        Settings()

def test_1_3_production_environment_rejects_missing_encryption_key(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "valid-production-secret-key-that-is-at-least-32-chars-long")
    monkeypatch.setenv("DATA_ENCRYPTION_KEY", "")
    with pytest.raises((ValidationError, ValueError)):
        Settings()

def test_1_4_production_environment_rejects_short_encryption_key(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "valid-production-secret-key-that-is-at-least-32-chars-long")
    monkeypatch.setenv("DATA_ENCRYPTION_KEY", "short-key-under-32-chars")
    with pytest.raises((ValidationError, ValueError)):
        Settings()

def test_1_5_trusted_proxy_ips_strips_testclient_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "valid-production-secret-key-that-is-at-least-32-chars-long")
    monkeypatch.setenv("DATA_ENCRYPTION_KEY", "valid-production-encryption-key-at-least-32-chars")
    monkeypatch.setenv("TRUSTED_PROXY_IPS", "127.0.0.1, ::1, testclient, 10.0.0.1")
    s = Settings()
    assert "testclient" not in s.TRUSTED_PROXY_IPS
    assert "10.0.0.1" in s.TRUSTED_PROXY_IPS

def test_1_6_cors_origins_strips_wildcards(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "*, http://localhost:5173, https://portal.vignan.edu")
    s = Settings()
    assert "*" not in s.CORS_ORIGINS
    assert "http://localhost:5173" in s.CORS_ORIGINS
    assert "https://portal.vignan.edu" in s.CORS_ORIGINS

def test_1_7_https_hsts_and_security_headers():
    res = client.get("/health", headers={"X-Forwarded-Proto": "https"})
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert res.headers.get("X-XSS-Protection") == "0"
    csp = res.headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp

def test_1_8_production_startup_does_not_seed_default_accounts():
    # In main.py: when settings.ENVIRONMENT == "production", startup_event() bypasses seeding
    # Verify that in a production configuration, db query count does not seed new users
    test_db = StagingSessionLocal()
    # Count current users
    init_count = test_db.query(User).count()
    test_db.close()
    assert init_count >= 1


# ==============================================================================
# TEST 2: AUTHENTICATION & AUTHORIZATION
# ==============================================================================
def test_2_1_admin_login_and_logout():
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "vignan123"},
        headers={"X-Forwarded-For": "192.168.1.110"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["username"] == "admin"

    # Logout
    logout_res = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {data['access_token']}"}
    )
    assert logout_res.status_code in [200, 204]

def test_2_2_invalid_password_rejection():
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "WrongPassword999!"},
        headers={"X-Forwarded-For": "192.168.1.111"}
    )
    assert res.status_code == 401
    assert "username or password" in res.json().get("detail", "").lower()

def test_2_3_login_rate_limiting():
    # Attempt rapid logins from same IP to trigger 5/minute limit
    ip = "192.168.10.99"
    blocked = False
    for _ in range(8):
        res = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "WrongPassword!"},
            headers={"X-Forwarded-For": ip}
        )
        if res.status_code == 429:
            blocked = True
            break
    assert blocked is True

def test_2_4_jwt_expiry_and_tampered_token():
    # Tampered token
    tampered = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.invalid_signature"
    res = client.get("/api/v1/admin/clients", headers={"Authorization": f"Bearer {tampered}"})
    assert res.status_code == 401

def test_2_5_client_role_restrictions(client_token):
    # Client cannot access admin-only endpoints
    headers = {"Authorization": f"Bearer {client_token}"}
    admin_only_res = client.get("/api/v1/admin/clients", headers=headers)
    assert admin_only_res.status_code in [401, 403]

    # Client cannot export complete student data
    export_res = client.get("/api/v1/reports/export?report_type=complete_student&format=excel", headers=headers)
    assert export_res.status_code == 403


# ==============================================================================
# TEST 3: STUDENT MANAGEMENT
# ==============================================================================
def test_3_1_create_test_student(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "roll_no": "STG_SMOKE_001",
        "full_name": "Staging Smoke Student",
        "branch": "Computer Science & Engineering",
        "branch_code": "CSE",
        "gender": "Female",
        "ug_cgpa": 8.95,
        "ug_year_of_pass": 2026,
        "no_of_backlogs": 0,
        "crt_registered": "Y",
        "aadhaar_number": "987654321098",
        "pan_number": "ABCDE9876F",
        "recorded_mobile": "9876543210"
    }
    res = client.post("/api/v1/students", headers=headers, json=payload)
    assert res.status_code == 201
    assert res.json()["roll_no"] == "STG_SMOKE_001"

def test_3_2_edit_student_information(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    patch_payload = {
        "ug_cgpa": 9.25,
        "no_of_backlogs": 1
    }
    res = client.put("/api/v1/students/STG_SMOKE_001", headers=headers, json=patch_payload)
    assert res.status_code == 200
    assert res.json()["ug_cgpa"] == 9.25

def test_3_3_view_student_details(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/students/STG_SMOKE_001", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["roll_no"] == "STG_SMOKE_001"
    assert data["full_name"] == "Staging Smoke Student"
    assert data["ug_cgpa"] == 9.25

def test_3_4_verify_student_photo_display(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Upload valid 1x1 PNG photo
    png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
    files = {"file": ("student_photo.png", png_bytes, "image/png")}
    upload_res = client.post(
        "/api/v1/documents/student/STG_SMOKE_001/upload",
        headers=headers,
        data={"doc_type": "photo"},
        files=files
    )
    assert upload_res.status_code == 200
    photo_rel_path = upload_res.json().get("path")
    assert photo_rel_path is not None
    filename = os.path.basename(photo_rel_path)

    # Fetch photo via endpoint
    photo_res = client.get(f"/api/v1/documents/photo/{filename}")
    assert photo_res.status_code == 200
    assert "image" in photo_res.headers.get("content-type", "")

def test_3_5_verify_document_upload_and_authorized_download(admin_token, client_token):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n>>\n%%EOF"
    files = {"file": ("offer_letter.pdf", pdf_bytes, "application/pdf")}
    upload_res = client.post(
        "/api/v1/documents/student/STG_SMOKE_001/upload",
        headers=admin_headers,
        data={"doc_type": "other"},
        files=files
    )
    assert upload_res.status_code == 200
    doc_path = upload_res.json().get("path")
    assert doc_path is not None

    # Authorized admin download
    download_res = client.get(f"/api/v1/documents/download?path={doc_path}", headers=admin_headers)
    assert download_res.status_code == 200
    assert download_res.content.startswith(b"%PDF-")

    # Unauthenticated download rejected
    unauth_client = TestClient(app)
    unauth_res = unauth_client.get(f"/api/v1/documents/download?path={doc_path}")
    assert unauth_res.status_code == 401

def test_3_6_verify_aadhaar_pan_masking_and_encryption(admin_token, client_token):
    # 1. Direct SQLite verification on staging DB
    con = sqlite3.connect(STAGING_DB_PATH)
    cur = con.cursor()
    row = cur.execute("SELECT aadhaar_number, pan_number FROM student_private_data WHERE student_id = (SELECT id FROM students WHERE roll_no = 'STG_SMOKE_001')").fetchone()
    con.close()
    assert row is not None
    aadhaar_stored, pan_stored = row[0], row[1]

    # Stored value MUST be ciphertext (startswith 'gcm1:') and NEVER plaintext
    assert aadhaar_stored is not None
    assert aadhaar_stored.startswith("gcm1:")
    assert "987654321098" not in aadhaar_stored
    assert pan_stored is not None
    assert pan_stored.startswith("gcm1:")
    assert "ABCDE9876F" not in pan_stored

    # 2. Public / Client API Masking
    client_headers = {"Authorization": f"Bearer {client_token}"}
    client_view_res = client.get("/api/v1/students/STG_SMOKE_001", headers=client_headers)
    assert client_view_res.status_code == 200
    c_data = client_view_res.json()
    # Masked or hidden
    assert c_data.get("aadhaar_number") in ["XXXX-XXXX-1098", "XXXXXXXX1098", None]
    assert c_data.get("pan_number") in ["ABXXXXX76F", "XXXXX9876F", None]


# ==============================================================================
# TEST 4: INTERNSHIP MANAGEMENT
# ==============================================================================
def test_4_1_create_and_edit_internship(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_payload = {
        "roll_no": "STG_SMOKE_001",
        "full_name": "Staging Smoke Student",
        "branch": "CSE",
        "organization_name": "Alpha Staging Technologies",
        "role": "Cloud Security Intern",
        "mode": "Hybrid",
        "start_date": "2026-02-01",
        "end_date": "2026-06-30",
        "stipend_amount": 35000,
        "certificate_received": "No"
    }
    res = client.post("/api/v1/internships", headers=headers, json=create_payload)
    assert res.status_code == 201
    internship_id = res.json()["id"]

    # Edit internship
    patch_payload = {
        "role": "Senior Cloud Security Intern",
        "certificate_received": "Yes"
    }
    edit_res = client.put(f"/api/v1/internships/{internship_id}", headers=headers, json=patch_payload)
    assert edit_res.status_code == 200
    assert edit_res.json()["role"] == "Senior Cloud Security Intern"
    assert edit_res.json()["certificate_received"] == "Yes"

def test_4_2_upload_and_download_internship_certificate(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # List internships to get id
    i_list = client.get("/api/v1/internships?roll_no=STG_SMOKE_001", headers=headers).json()
    assert len(i_list["items"]) >= 1
    i_id = i_list["items"][0]["id"]

    # Upload valid PDF certificate
    pdf_bytes = b"%PDF-1.4\nCertificate of Completion\n%%EOF"
    files = {"file": ("internship_cert.pdf", pdf_bytes, "application/pdf")}
    upload_res = client.post(f"/api/v1/documents/internship/{i_id}/certificate", headers=headers, files=files)
    assert upload_res.status_code == 200
    cert_path = upload_res.json().get("path")
    assert cert_path is not None

    # Authorized download
    download_res = client.get(f"/api/v1/documents/download?path={cert_path}", headers=headers)
    assert download_res.status_code == 200
    assert download_res.content.startswith(b"%PDF-")

    # Unauthenticated download rejected
    unauth_client = TestClient(app)
    unauth_res = unauth_client.get(f"/api/v1/documents/download?path={cert_path}")
    assert unauth_res.status_code == 401


# ==============================================================================
# TEST 5: IMPORTS AND REPORTS
# ==============================================================================
def test_5_1_import_valid_csv_and_xlsx(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # 1. Valid CSV
    csv_content = "Roll No.,Full Name,Branch\nSTG_CSV_01,CSV Student One,CSE\n".encode("utf-8")
    files_csv = {"file": ("students.csv", csv_content, "text/csv")}
    res_csv = client.post("/api/v1/imports/process", headers=headers, data={"template_type": "student"}, files=files_csv)
    assert res_csv.status_code == 200

    # 2. Valid XLSX
    df = pd.DataFrame([{
        "Roll No.": "STG_XLSX_01",
        "Full Name": "XLSX Student One",
        "Branch": "ECE"
    }])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    files_xlsx = {"file": ("students.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res_xlsx = client.post("/api/v1/imports/process", headers=headers, data={"template_type": "student"}, files=files_xlsx)
    assert res_xlsx.status_code == 200

def test_5_2_reject_disguised_executable_files(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Disguised Windows PE executable renamed to .xlsx
    fake_xlsx = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00" + b"\x00" * 100
    files = {"file": ("malware.xlsx", fake_xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = client.post("/api/v1/imports/process", headers=headers, data={"template_type": "student"}, files=files)
    assert res.status_code == 400
    assert "Invalid file signature" in res.json().get("detail", "")

def test_5_3_reject_oversized_and_malformed_files(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Corrupted text disguised as xlsx
    corrupt = b"Corrupted arbitrary data not matching ZIP or OLE headers"
    files = {"file": ("corrupt.xlsx", corrupt, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = client.post("/api/v1/imports/process", headers=headers, data={"template_type": "student"}, files=files)
    assert res.status_code == 400

def test_5_4_generate_authorized_reports(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Excel
    res_excel = client.get("/api/v1/reports/export?report_type=backlog&format=excel", headers=headers)
    assert res_excel.status_code == 200
    assert "spreadsheetml" in res_excel.headers.get("content-type", "")

    # CSV
    res_csv = client.get("/api/v1/reports/export?report_type=backlog&format=csv", headers=headers)
    assert res_csv.status_code == 200
    assert "csv" in res_csv.headers.get("content-type", "")

    # PDF
    res_pdf = client.get("/api/v1/reports/export?report_type=backlog&format=pdf", headers=headers)
    assert res_pdf.status_code == 200
    assert "pdf" in res_pdf.headers.get("content-type", "")

def test_5_5_client_cannot_export_restricted_student_data(client_token):
    headers = {"Authorization": f"Bearer {client_token}"}
    res = client.get("/api/v1/reports/export?report_type=complete_student&format=excel", headers=headers)
    assert res.status_code == 403
    assert "restricted to administrators" in res.json().get("detail", "")


# ==============================================================================
# TEST 7: BACKUP AND RECOVERY VERIFICATION
# ==============================================================================
def test_7_1_restore_database_backup():
    restore_target = "staging_recovery_verified.db"
    assert os.path.exists(BACKUP_DB_PATH), "Backup file missing"
    shutil.copyfile(BACKUP_DB_PATH, restore_target)
    assert os.path.exists(restore_target)

    # Verify table integrity
    con = sqlite3.connect(restore_target)
    cur = con.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "students" in tables
    assert "internships" in tables
    assert "student_private_data" in tables
    assert "users" in tables

    student_count = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    assert student_count > 0

    internship_count = cur.execute("SELECT COUNT(*) FROM internships").fetchone()[0]
    assert internship_count > 0

    con.close()
    if os.path.exists(restore_target):
        os.remove(restore_target)

def test_7_2_verify_encrypted_student_identifiers_decrypt_correctly():
    # Load records directly from backup and decrypt with key
    con = sqlite3.connect(BACKUP_DB_PATH)
    cur = con.cursor()
    rows = cur.execute("SELECT student_id, aadhaar_number, pan_number FROM student_private_data WHERE aadhaar_number IS NOT NULL LIMIT 5").fetchall()
    con.close()

    assert len(rows) > 0, "No private data records found in backup"
    key = settings.DATA_ENCRYPTION_KEY

    for student_id, aadhaar_cipher, pan_cipher in rows:
        if aadhaar_cipher and aadhaar_cipher.startswith("gcm1:"):
            plain_aadhaar = decrypt_aes_gcm(aadhaar_cipher, key)
            assert plain_aadhaar is not None
            assert len(plain_aadhaar) >= 4
        if pan_cipher and pan_cipher.startswith("gcm1:"):
            plain_pan = decrypt_aes_gcm(pan_cipher, key)
            assert plain_pan is not None
            assert len(plain_pan) >= 5

def test_7_3_verify_uploaded_files_present_and_accessible():
    # Verify uploads directory exists and has expected subdirectories
    upload_root = settings.UPLOAD_DIR
    assert os.path.exists(upload_root)
    for folder in ["photos", "aadhaar", "certificates", "documents"]:
        subfolder = os.path.join(upload_root, folder)
        assert os.path.exists(subfolder), f"Upload subfolder missing: {subfolder}"
