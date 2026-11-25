import uuid
import pytest
import sqlite3
import os
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.database import SessionLocal
from app.models.student import Student, StudentPrivateData
from app.utils.crypto import encrypt_aes_gcm, decrypt_aes_gcm, encrypt_data, decrypt_data
from app.utils.security import verify_file_signature, hash_password
from app.cli import bootstrap_admin
from app.models.user import User

client = TestClient(app)

@pytest.fixture(scope="module")
def admin_token():
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "vignan123"},
        headers={"X-Forwarded-For": "10.10.1.1"}
    )
    if res.status_code != 200:
        res = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "ChangeMe123!"},
            headers={"X-Forwarded-For": "10.10.1.1"}
        )
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def client_token():
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "client", "password": "Client123!"},
        headers={"X-Forwarded-For": "10.10.1.2"}
    )
    assert res.status_code == 200, f"Client login failed: {res.text}"
    return res.json()["access_token"]


# ==============================================================================
# 1. FIX 1 (F-06): Protected Bulk Student Reports & Role Masking
# ==============================================================================
def test_f06_complete_student_export_restricted_to_admin(admin_token, client_token):
    # Admin is authorized to export complete_student
    res_admin = client.get(
        "/api/v1/reports/export?report_type=complete_student&format=excel",
        headers={"Authorization": f"Bearer {admin_token}", "X-Forwarded-For": "10.10.1.10"}
    )
    assert res_admin.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in res_admin.headers.get("content-type", "")

    # Client role MUST be forbidden (HTTP 403) from complete_student export
    res_client = client.get(
        "/api/v1/reports/export?report_type=complete_student&format=excel",
        headers={"Authorization": f"Bearer {client_token}", "X-Forwarded-For": "10.10.1.11"}
    )
    assert res_client.status_code == 403
    assert "Forbidden" in res_client.json().get("detail", "") or "restricted" in res_client.json().get("detail", "").lower()

def test_f06_client_report_export_masks_sensitive_data(client_token):
    # Non-admin roles (CLIENT) can export standard summary reports, but PII must be masked
    res = client.get(
        "/api/v1/reports/export?report_type=without_internships&format=excel",
        headers={"Authorization": f"Bearer {client_token}", "X-Forwarded-For": "10.10.1.12"}
    )
    assert res.status_code == 200
    # Export returns binary excel; verify backend service masking logic directly
    from app.services.report_service import generate_report_dataframe
    db = SessionLocal()
    try:
        df_masked = generate_report_dataframe(db, "without_internships", mask_sensitive=True)
        if not df_masked.empty and "Contact" in df_masked.columns:
            for val in df_masked["Contact"].dropna():
                if val:
                    assert "XXXX" in str(val) or len(str(val)) <= 4, f"Contact was not properly masked: {val}"
    finally:
        db.close()


# ==============================================================================
# 2. FIX 2 (F-04): Authenticated AES-256-GCM Encryption at Rest for Aadhaar & PAN
# ==============================================================================
def test_f04_aadhaar_pan_stored_as_aes_256_gcm_ciphertext(admin_token):
    roll_no = f"P2_CRY_{uuid.uuid4().hex[:8].upper()}"
    raw_aadhaar = "987654321098"
    raw_pan = "ABCDE1234F"

    # Create a student with private data
    res = client.post(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {admin_token}", "X-Forwarded-For": "10.10.1.20"},
        json={
            "roll_no": roll_no,
            "full_name": "Encryption Verification Student",
            "branch": "CSE",
            "aadhaar_number": raw_aadhaar,
            "pan_number": raw_pan,
        }
    )
    assert res.status_code in [200, 201]

    # Verify directly against raw SQLite database (bypassing ORM decryptor)
    conn = sqlite3.connect("student_portal.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.aadhaar_number, p.pan_number 
        FROM student_private_data p
        JOIN students s ON s.id = p.student_id
        WHERE s.roll_no = ?
    """, (roll_no,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "Private data row not found in raw SQLite table"
    stored_aadhaar, stored_pan = row

    # Must be encrypted with gcm1: prefix
    assert stored_aadhaar.startswith("gcm1:"), f"Aadhaar is not encrypted: {stored_aadhaar}"
    assert stored_pan.startswith("gcm1:"), f"PAN is not encrypted: {stored_pan}"

    # Plaintext must never match raw database content
    assert raw_aadhaar not in stored_aadhaar
    assert raw_pan not in stored_pan

    # Decryption via crypto utility must recover original value
    assert decrypt_data(stored_aadhaar) == raw_aadhaar
    assert decrypt_data(stored_pan) == raw_pan

def test_f04_crypto_idempotence_and_double_encryption_prevention():
    secret = "998877665544"
    encrypted1 = encrypt_data(secret)
    assert encrypted1.startswith("gcm1:")
    # Re-encrypting should return identical string, preventing double encryption
    encrypted2 = encrypt_data(encrypted1)
    assert encrypted1 == encrypted2
    assert decrypt_data(encrypted2) == secret


# ==============================================================================
# 3. FIX 3 (F-07): Secure Default Account Seeding & Admin CLI Bootstrap
# ==============================================================================
def test_f07_cli_bootstrap_admin_creates_super_admin():
    test_user = f"cli_admin_{uuid.uuid4().hex[:6]}"
    test_email = f"{test_user}@institution.edu"
    test_pass = "SecureAdminPass#2026"

    bootstrap_admin(username=test_user, email=test_email, password=test_pass, force=True)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == test_user).first()
        assert user is not None
        assert user.role == "SUPER_ADMIN"
        assert user.email == test_email
        assert user.hashed_password != test_pass  # Must be hashed
    finally:
        db.close()


# ==============================================================================
# 4. FIX 4 (F-09): File Signature Verification & Upload Protection
# ==============================================================================
def test_f09_verify_file_signature_accepts_valid_types():
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    jpg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3"
    csv_bytes = b"roll_no,full_name,branch\n123,Test,CSE\n"

    assert verify_file_signature(png_bytes, "photo.png") is True
    assert verify_file_signature(jpg_bytes, "cert.jpg") is True
    assert verify_file_signature(pdf_bytes, "doc.pdf") is True
    assert verify_file_signature(csv_bytes, "data.csv") is True

def test_f09_verify_file_signature_rejects_disguised_or_malicious_files():
    # PE executable renamed to .png
    fake_png = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff"
    assert verify_file_signature(fake_png, "malware.png") is False

    # Plain text file renamed to .pdf
    fake_pdf = b"Hello world, I am plain text!"
    assert verify_file_signature(fake_pdf, "document.pdf") is False

    # Disallowed executable extension
    assert verify_file_signature(b"echo 1", "script.sh") is False

def test_f09_upload_rejects_disguised_file(admin_token):
    roll_no = f"P2_DISG_{uuid.uuid4().hex[:8].upper()}"
    headers = {"Authorization": f"Bearer {admin_token}", "X-Forwarded-For": "10.10.1.40"}

    # Create dummy student
    client.post("/api/v1/students", headers=headers, json={
        "roll_no": roll_no, "full_name": "Disguised File Student", "branch": "CSE"
    })

    # Disguised file: text bytes uploaded with .jpg extension
    corrupt_data = b"This is plain text pretending to be a JPG"
    files = {"file": ("malicious.jpg", corrupt_data, "image/jpeg")}

    res = client.post(
        f"/api/v1/documents/student/{roll_no}/upload",
        headers=headers,
        data={"doc_type": "photo"},
        files=files
    )
    assert res.status_code == 400
    assert "Invalid file signature" in res.json().get("detail", "")


# ==============================================================================
# 5. FIX 5 (F-03): Login Rate Limiting (5 requests/minute per client IP)
# ==============================================================================
def test_f03_login_rate_limiting_enforced():
    rate_test_ip = f"198.51.100.{uuid.uuid4().int % 200 + 10}"
    rate_headers = {"X-Forwarded-For": rate_test_ip}

    # First 5 login attempts should process normally (returning 401 for bad password)
    for i in range(5):
        res = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrong_password_test"},
            headers=rate_headers
        )
        assert res.status_code in [401, 200], f"Attempt {i+1} failed with status {res.status_code}"

    # 6th attempt within the minute MUST return HTTP 429 Too Many Requests
    blocked_res = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong_password_test"},
        headers=rate_headers
    )
    assert blocked_res.status_code == 429, f"Expected 429 on 6th attempt, got {blocked_res.status_code}: {blocked_res.text}"

def test_f03_trusted_proxy_with_valid_forwarded_ip():
    from app.limiter import get_real_client_ip
    from starlette.requests import Request

    # Trusted proxy peer (127.0.0.1)
    scope = {
        "type": "http",
        "client": ("127.0.0.1", 54321),
        "headers": [(b"x-forwarded-for", b"203.0.113.10")],
    }
    req = Request(scope)
    assert get_real_client_ip(req) == "203.0.113.10"

def test_f03_untrusted_client_with_forged_x_forwarded_for():
    from app.limiter import get_real_client_ip
    from starlette.requests import Request

    # Untrusted client direct connection (198.51.100.55)
    scope = {
        "type": "http",
        "client": ("198.51.100.55", 54321),
        "headers": [(b"x-forwarded-for", b"10.0.0.1")],
    }
    req = Request(scope)
    # Forged X-Forwarded-For must be completely ignored; actual peer IP must be used
    assert get_real_client_ip(req) == "198.51.100.55"

def test_f03_untrusted_client_with_forged_x_real_ip():
    from app.limiter import get_real_client_ip
    from starlette.requests import Request

    scope = {
        "type": "http",
        "client": ("198.51.100.56", 54321),
        "headers": [(b"x-real-ip", b"10.0.0.2")],
    }
    req = Request(scope)
    # Forged X-Real-IP must be completely ignored
    assert get_real_client_ip(req) == "198.51.100.56"

def test_f03_malformed_forwarded_ip_safely_falls_back():
    from app.limiter import get_real_client_ip
    from starlette.requests import Request

    scope = {
        "type": "http",
        "client": ("127.0.0.1", 54321),
        "headers": [(b"x-forwarded-for", b"not-a-valid-ip-address")],
    }
    req = Request(scope)
    # Malformed IP must safely fall back to peer IP without crashing
    assert get_real_client_ip(req) == "127.0.0.1"

def test_f03_empty_forwarded_headers_safely_falls_back():
    from app.limiter import get_real_client_ip
    from starlette.requests import Request

    scope = {
        "type": "http",
        "client": ("127.0.0.1", 54321),
        "headers": [(b"x-forwarded-for", b"   ")],
    }
    req = Request(scope)
    assert get_real_client_ip(req) == "127.0.0.1"

def test_f03_multiple_forwarded_ip_values():
    from app.limiter import get_real_client_ip
    from starlette.requests import Request

    scope = {
        "type": "http",
        "client": ("127.0.0.1", 54321),
        "headers": [(b"x-forwarded-for", b"203.0.113.88, 10.0.0.1, 192.168.1.50")],
    }
    req = Request(scope)
    # Outermost client IP is selected
    assert get_real_client_ip(req) == "203.0.113.88"

def test_f03_untrusted_client_cannot_bypass_limits_by_rotating_headers():
    untrusted_peer = f"198.51.100.{uuid.uuid4().int % 100 + 100}"
    untrusted_client = TestClient(app, client=(untrusted_peer, 50000))

    # Send 5 failed login attempts from untrusted peer, each pretending to be a different IP
    for i in range(5):
        forged_ip = f"10.99.{i}.{i+1}"
        res = untrusted_client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrong_password"},
            headers={"X-Forwarded-For": forged_ip, "X-Real-IP": forged_ip}
        )
        assert res.status_code == 401

    # 6th attempt from the same untrusted peer (even with yet another forged header) MUST be blocked
    blocked_res = untrusted_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong_password"},
        headers={"X-Forwarded-For": "10.99.99.99", "X-Real-IP": "10.99.99.99"}
    )
    assert blocked_res.status_code == 429, f"Attacker bypassed rate limit via header spoofing! Status: {blocked_res.status_code}"


# ==============================================================================
# 6. FIX 6 (F-10): HTTP Security Response Headers
# ==============================================================================
def test_f10_http_security_headers_present():
    res = client.get("/health", headers={"X-Forwarded-For": "10.10.1.60"})
    assert res.status_code == 200

    headers = res.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert headers.get("X-XSS-Protection") == "0"
    assert "Content-Security-Policy" in headers
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")


# ==============================================================================
# 7. Production Hardening: Legacy Import Validation
# ==============================================================================
def test_legacy_import_rejects_disguised_file(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}", "X-Forwarded-For": "10.10.1.70"}
    corrupt_data = b"This is plain text disguised as an Excel workbook"
    files = {"file": ("malicious_grades.xlsx", corrupt_data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

    res = client.post(
        "/api/v1/imports/process",
        headers=headers,
        data={"template_type": "student"},
        files=files
    )
    assert res.status_code == 400
    assert "Invalid file signature" in res.json().get("detail", "")

def test_legacy_import_rejects_unsupported_extension(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}", "X-Forwarded-For": "10.10.1.71"}
    files = {"file": ("script.py", b"print('exploit')", "text/x-python")}

    res = client.post(
        "/api/v1/imports/process",
        headers=headers,
        data={"template_type": "student"},
        files=files
    )
    assert res.status_code == 400
    assert "Only .xlsx, .xls, and .csv" in res.json().get("detail", "")


# ==============================================================================
# 8. Production Hardening: Explicit Cryptographic Error Handling
# ==============================================================================
def test_crypto_incorrect_key_raises_explicit_decryption_error(monkeypatch):
    from app.utils.crypto import encrypt_aes_gcm, decrypt_aes_gcm, DecryptionError

    secret = "987654321098"
    ciphertext = encrypt_aes_gcm(secret)

    # Change encryption key to a completely different 32-character key
    monkeypatch.setattr(settings, "DATA_ENCRYPTION_KEY", "different-secret-key-012345678901")

    with pytest.raises(DecryptionError, match="Decryption failed"):
        decrypt_aes_gcm(ciphertext)

def test_crypto_corrupted_ciphertext_raises_explicit_decryption_error():
    from app.utils.crypto import encrypt_aes_gcm, decrypt_aes_gcm, DecryptionError

    ciphertext = encrypt_aes_gcm("ABCDE1234F")
    parts = ciphertext.split(":")
    # Corrupt last byte of ciphertext/tag
    corrupted_ct = parts[2][:-2] + ("00" if parts[2][-2:] != "00" else "ff")
    tampered_ciphertext = f"gcm1:{parts[1]}:{corrupted_ct}"

    with pytest.raises(DecryptionError, match="Decryption failed"):
        decrypt_aes_gcm(tampered_ciphertext)

def test_saving_unrelated_student_fields_preserves_encrypted_identifiers(admin_token):
    roll_no = f"P2_PRE_{uuid.uuid4().hex[:8].upper()}"
    raw_aadhaar = "998877665544"
    raw_pan = "PQRST5678X"
    headers = {"Authorization": f"Bearer {admin_token}", "X-Forwarded-For": "10.10.1.75"}

    # 1. Create student with private identifiers
    create_res = client.post(
        "/api/v1/students",
        headers=headers,
        json={
            "roll_no": roll_no,
            "full_name": "Identifier Preservation Test",
            "branch": "CSE",
            "aadhaar_number": raw_aadhaar,
            "pan_number": raw_pan,
        }
    )
    assert create_res.status_code in [200, 201]

    # 2. Update an unrelated field (e.g. full_name)
    update_res = client.put(
        f"/api/v1/students/{roll_no}",
        headers=headers,
        json={"full_name": "Updated Identifier Preservation Test"}
    )
    assert update_res.status_code == 200

    # 3. Verify in raw SQLite: identifiers MUST still be encrypted with gcm1: and decrypt to original value
    conn = sqlite3.connect("student_portal.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.aadhaar_number, p.pan_number
        FROM student_private_data p
        JOIN students s ON s.id = p.student_id
        WHERE s.roll_no = ?
    """, (roll_no,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    stored_aadhaar, stored_pan = row
    assert stored_aadhaar.startswith("gcm1:")
    assert stored_pan.startswith("gcm1:")
    assert decrypt_data(stored_aadhaar) == raw_aadhaar
    assert decrypt_data(stored_pan) == raw_pan


# ==============================================================================
# 9. Production Hardening: Trusted Proxy Excludes testclient in Production
# ==============================================================================
def test_trusted_proxy_excludes_testclient_in_production(monkeypatch):
    from app.config import Settings
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "x" * 32)
    monkeypatch.setenv("DATA_ENCRYPTION_KEY", "y" * 32)
    s = Settings()
    assert "testclient" not in s.TRUSTED_PROXY_IPS
    assert "127.0.0.1" in s.TRUSTED_PROXY_IPS

