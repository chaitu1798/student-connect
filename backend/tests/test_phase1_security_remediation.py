import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

@pytest.fixture(scope="module")
def admin_token():
    # Login as admin using default administrative password
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "vignan123"})
    if res.status_code != 200:
        res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def client_token():
    res = client.post("/api/v1/auth/login", json={"username": "client", "password": "Client123!"})
    assert res.status_code == 200, f"Client login failed: {res.text}"
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def setup_test_student_and_docs(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    roll_no = f"P1_SEC_{uuid.uuid4().hex[:8].upper()}"

    # Create student
    s_res = client.post("/api/v1/students", headers=headers, json={
        "roll_no": roll_no,
        "full_name": "Phase1 Security Test Student",
        "branch": "CSE"
    })
    assert s_res.status_code in [200, 201]

    # Upload Aadhaar
    dummy_img = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00"
    files = {"file": ("aadhaar_test.jpg", dummy_img, "image/jpeg")}
    up_res = client.post(f"/api/v1/documents/student/{roll_no}/upload", headers=headers, data={"doc_type": "aadhaar"}, files=files)
    assert up_res.status_code == 200
    aadhaar_path = up_res.json()["path"]

    # Upload photo
    files_photo = {"file": ("photo_test.jpg", dummy_img, "image/jpeg")}
    photo_res = client.post(f"/api/v1/documents/student/{roll_no}/upload", headers=headers, data={"doc_type": "photo"}, files=files_photo)
    assert photo_res.status_code == 200
    photo_path = photo_res.json()["path"]

    return {
        "roll_no": roll_no,
        "aadhaar_path": aadhaar_path,
        "photo_path": photo_path,
    }


# ==============================================================================
# TEST 1: dev_auth=admin cannot bypass authentication
# ==============================================================================
def test_1_dev_auth_parameter_cannot_bypass_authentication():
    client.cookies.clear()
    endpoints = [
        "/api/v1/admin/students?dev_auth=admin",
        "/api/v1/students?dev_auth=admin",
        "/api/v1/admin/clients?dev_auth=admin",
        "/api/v1/admin/permissions?dev_auth=admin",
    ]
    for endpoint in endpoints:
        res = client.get(endpoint)
        assert res.status_code == 401, f"Expected 401 on {endpoint}, got {res.status_code}"
        assert res.json()["detail"] in ["Not authenticated", "Could not validate credentials"]


# ==============================================================================
# TEST 2: dev-admin-token cannot grant administrator access
# ==============================================================================
def test_2_dev_admin_token_cannot_grant_admin_access():
    client.cookies.clear()
    headers = {"Authorization": "Bearer dev-admin-token"}
    endpoints = [
        "/api/v1/admin/students",
        "/api/v1/students",
        "/api/v1/admin/permissions",
    ]
    for endpoint in endpoints:
        res = client.get(endpoint, headers=headers)
        assert res.status_code == 401, f"Expected 401 with dev-admin-token on {endpoint}, got {res.status_code}"


# ==============================================================================
# TEST 3: Untrusted origins are rejected by CORS
# ==============================================================================
def test_3_untrusted_origins_rejected_by_cors():
    headers = {
        "Origin": "https://attacker-controlled-origin.com",
        "Access-Control-Request-Method": "GET",
    }
    res = client.options("/api/v1/admin/students", headers=headers)
    allowed_origin = res.headers.get("access-control-allow-origin")
    assert allowed_origin != "https://attacker-controlled-origin.com", (
        f"Untrusted origin was allowed by CORS: {allowed_origin}"
    )
    assert allowed_origin != "*", "Wildcard origin cannot be allowed when credentials are used"


# ==============================================================================
# TEST 4: Trusted frontend origins continue working
# ==============================================================================
def test_4_trusted_origins_allowed_by_cors():
    trusted = "http://localhost:5173"
    headers = {
        "Origin": trusted,
        "Access-Control-Request-Method": "GET",
    }
    res = client.options("/api/v1/admin/students", headers=headers)
    assert res.headers.get("access-control-allow-origin") == trusted
    assert res.headers.get("access-control-allow-credentials") == "true"


# ==============================================================================
# TEST 5: Unauthenticated document requests return HTTP 401
# ==============================================================================
def test_5_unauthenticated_document_requests_return_401(setup_test_student_and_docs):
    client.cookies.clear()
    photo_path = setup_test_student_and_docs["photo_path"]
    aadhaar_path = setup_test_student_and_docs["aadhaar_path"]

    # /view
    res1 = client.get(f"/api/v1/documents/view?path={photo_path}")
    assert res1.status_code == 401, f"Expected 401 on /view without auth, got {res1.status_code}"

    # /download
    res2 = client.get(f"/api/v1/documents/download?path={aadhaar_path}")
    assert res2.status_code == 401, f"Expected 401 on /download without auth, got {res2.status_code}"

    # /photo/{filename}
    filename = photo_path.split("/")[-1]
    res3 = client.get(f"/api/v1/documents/photo/{filename}")
    assert res3.status_code == 401, f"Expected 401 on /photo without auth, got {res3.status_code}"


# ==============================================================================
# TEST 6: Unauthorized document access returns HTTP 403
# ==============================================================================
def test_6_unauthorized_document_access_returns_403(client_token, setup_test_student_and_docs):
    headers = {"Authorization": f"Bearer {client_token}"}
    aadhaar_path = setup_test_student_and_docs["aadhaar_path"]

    # Client role attempting to view or download Aadhaar
    res_view = client.get(f"/api/v1/documents/view?path={aadhaar_path}", headers=headers)
    assert res_view.status_code == 403, f"Expected 403 for client accessing Aadhaar on /view, got {res_view.status_code}"

    res_dl = client.get(f"/api/v1/documents/download?path={aadhaar_path}", headers=headers)
    assert res_dl.status_code == 403, f"Expected 403 for client accessing Aadhaar on /download, got {res_dl.status_code}"


# ==============================================================================
# TEST 7: Authorized administrators can view permitted documents
# ==============================================================================
def test_7_authorized_admin_can_view_permitted_documents(admin_token, setup_test_student_and_docs):
    headers = {"Authorization": f"Bearer {admin_token}"}
    aadhaar_path = setup_test_student_and_docs["aadhaar_path"]
    photo_path = setup_test_student_and_docs["photo_path"]

    res_view = client.get(f"/api/v1/documents/view?path={photo_path}", headers=headers)
    assert res_view.status_code == 200, f"Admin could not view photo: {res_view.status_code}"

    res_aadhaar = client.get(f"/api/v1/documents/download?path={aadhaar_path}", headers=headers)
    assert res_aadhaar.status_code == 200, f"Admin could not download Aadhaar: {res_aadhaar.status_code}"


# ==============================================================================
# TEST 8: Path traversal attempts are rejected
# ==============================================================================
def test_8_path_traversal_attempts_are_rejected(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    traversal_payloads = [
        "../../etc/passwd",
        "..\\..\\Windows\\win.ini",
        "documents/../../app/config.py",
        "/etc/shadow",
        "C:\\Windows\\System32\\drivers\\etc\\hosts",
        "documents/..%2f..%2fconfig.py",
    ]
    for payload in traversal_payloads:
        # /view
        res_v = client.get(f"/api/v1/documents/view?path={payload}", headers=headers)
        assert res_v.status_code in [400, 403, 404], f"Traversal succeeded on /view with {payload}: {res_v.status_code}"

        # /download
        res_d = client.get(f"/api/v1/documents/download?path={payload}", headers=headers)
        assert res_d in [400, 403, 404] or res_d.status_code in [400, 403, 404], (
            f"Traversal succeeded on /download with {payload}: {res_d.status_code}"
        )


# ==============================================================================
# TEST 9: Existing student CRUD functionality continues working
# ==============================================================================
def test_9_existing_student_crud_functionality(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    test_roll = f"P1_CRUD_{uuid.uuid4().hex[:8].upper()}"

    # Create
    create_res = client.post("/api/v1/students", headers=headers, json={
        "roll_no": test_roll,
        "full_name": "CRUD Verification Student",
        "branch": "IT",
        "ug_cgpa": 8.75
    })
    assert create_res.status_code in [200, 201]
    created = create_res.json()
    assert created["roll_no"] == test_roll
    assert created["ug_cgpa"] == 8.75

    # Read
    read_res = client.get(f"/api/v1/students/{test_roll}", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["full_name"] == "CRUD Verification Student"

    # Update (PATCH)
    patch_res = client.patch(f"/api/v1/students/{test_roll}", headers=headers, json={
        "ug_cgpa": 9.10,
        "contact_number": "9876543210"
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["ug_cgpa"] == 9.10

    # Delete / Archive
    del_res = client.delete(f"/api/v1/students/{test_roll}", headers=headers)
    assert del_res.status_code == 200

    # Verify archived
    verify_res = client.get(f"/api/v1/students/{test_roll}", headers=headers)
    assert verify_res.status_code == 404


# ==============================================================================
# TEST 10: Existing authentication and login functionality continue working
# ==============================================================================
def test_10_authentication_and_login_flow():
    # Valid login
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "vignan123"})
    if res.status_code != 200:
        res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"

    # Invalid login rejected
    bad_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrongpassword123"})
    assert bad_res.status_code == 401
    assert "Incorrect username or password" in bad_res.json()["detail"]
