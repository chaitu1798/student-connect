import pytest
import io
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.student import Student, StudentPublicationSetting
from app.utils.security import hash_password

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Reset admin password and must_change_password
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        admin.hashed_password = hash_password("ChangeMe123!")
        admin.must_change_password = True
        db.commit()
    db.close()

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_auth_login_refresh_logout_workflow():
    # 1. Login
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["must_change_password"] is True
    token = data["access_token"]
    refresh = data["refresh_token"]

    # 2. Refresh token
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert ref_res.status_code == 200
    assert "access_token" in ref_res.json()

    # 3. Change password
    chg_res = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={"old_password": "ChangeMe123!", "new_password": "SecurePassword2026!"}
    )
    assert chg_res.status_code == 200

    # 4. Re-login with new password
    login_new = client.post("/api/v1/auth/login", json={"username": "admin", "password": "SecurePassword2026!"})
    assert login_new.status_code == 200
    assert login_new.json()["user"]["must_change_password"] is False

    # 5. Reset password back for tests
    client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {login_new.json()['access_token']}"},
        json={"old_password": "SecurePassword2026!", "new_password": "ChangeMe123!"}
    )
    db = SessionLocal()
    adm = db.query(User).filter(User.username == "admin").first()
    if adm:
        adm.must_change_password = True
        db.commit()
    db.close()

def test_public_student_search_and_privacy():
    # Public search by roll number
    res = client.get("/api/v1/public/students/search?roll_number=21A91A0501")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["items"][0]["roll_no"] == "21A91A0501"

    # Public search by full name
    res2 = client.get("/api/v1/public/students/search?full_name=Rahul")
    assert res2.status_code == 200
    assert res2.json()["total"] >= 1

    # Public authorized profile view - ensure privacy
    res_prof = client.get("/api/v1/public/students/21A91A0501")
    assert res_prof.status_code == 200
    prof = res_prof.json()
    assert prof["roll_no"] == "21A91A0501"
    # Shielded fields must NEVER be returned to the public
    assert "aadhaar_number" not in prof
    assert "pan_number" not in prof
    assert "contact_number" not in prof
    assert "recorded_email" not in prof
    assert "full_residential_address" not in prof

def test_public_internships():
    res = client.get("/api/v1/public/internships")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 1
    assert "organization_name" in items[0]

def test_admin_student_crud():
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create student
    st_data = {
        "roll_no": "TEST_ROLL_99",
        "full_name": "TEST STUDENT ARCHIVE",
        "branch": "Computer Science & Engineering",
        "branch_code": "CSE",
        "column1": "LEGACY_TEST_NOTE",
        "ug_cgpa": 8.8,
        "ug_year_of_passing": 2026,
    }
    create_res = client.post("/api/v1/admin/students", headers=headers, json=st_data)
    assert create_res.status_code == 201
    st_id = create_res.json()["id"]

    # Patch student
    patch_res = client.patch(f"/api/v1/admin/students/{st_id}", headers=headers, json={"ug_cgpa": 9.2})
    assert patch_res.status_code == 200
    assert patch_res.json()["ug_cgpa"] == 9.2

    # Archive student
    arch_res = client.post(f"/api/v1/admin/students/{st_id}/archive", headers=headers)
    assert arch_res.status_code == 200

def test_staged_import_diff_and_approval_workflow():
    # Reset 21A91A0501 to baseline so diff detection is deterministic across repeated runs
    db = SessionLocal()
    st = db.query(Student).filter(Student.roll_no == "21A91A0501").first()
    if st:
        st.full_name = "Rahul Sharma"
        if st.academics:
            st.academics.ug_cgpa = 8.75
        db.commit()
    db.close()

    # 1. Client logs in
    client_res = client.post("/api/v1/auth/login", json={"username": "client", "password": "Client123!"})
    client_token = client_res.json()["access_token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}

    # 2. Client uploads an Excel document with proposed changes to 21A91A0501
    df = pd.DataFrame([
        {
            "Roll No.": "21A91A0501",
            "Full Name (As per SSC)": "SHARMA RAHUL KUMAR",
            "UG/B.Tech CGPA": 9.45,  # Proposed new CGPA
        }
    ])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    files = {"file": ("batch_update.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    stage_res = client.post("/api/v1/client/imports", headers=client_headers, data={"template_type": "student"}, files=files)
    assert stage_res.status_code == 201
    job = stage_res.json()
    job_id = job["id"]
    assert job["status"] == "DRAFT"

    # 3. Client previews the diff
    prev_res = client.get(f"/api/v1/client/imports/{job_id}/preview", headers=client_headers)
    assert prev_res.status_code == 200
    prev_data = prev_res.json()
    assert len(prev_data["rows"]) == 1
    # Verify diff detected
    assert prev_data["rows"][0]["status"] == "DIFF_DETECTED"
    field_names = [c["field_name"] for c in prev_data["rows"][0]["changes"]]
    assert "ug_cgpa" in field_names
    assert "full_name" in field_names

    # 4. Client submits for Admin approval
    sub_res = client.post(f"/api/v1/client/imports/{job_id}/submit", headers=client_headers)
    assert sub_res.status_code == 200

    # 5. Administrator views diff
    admin_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    diff_res = client.get(f"/api/v1/admin/imports/{job_id}/diff", headers=admin_headers)
    assert diff_res.status_code == 200
    assert diff_res.json()["total_diff_changes"] >= 1

    # 6. Administrator approves import
    appr_res = client.post(f"/api/v1/admin/imports/{job_id}/approve", headers=admin_headers, json={"remarks": "Approved 8th sem update"})
    assert appr_res.status_code == 200

    # 7. Verify master database was updated transactionally!
    st_res = client.get("/api/v1/admin/students/21A91A0501", headers=admin_headers)
    assert st_res.status_code == 200
    assert st_res.json()["ug_cgpa"] == 9.45

def test_admin_analytics_endpoints():
    admin_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    headers = {"Authorization": f"Bearer {admin_res.json()['access_token']}"}

    # Overview
    res_ov = client.get("/api/v1/admin/analytics/overview", headers=headers)
    assert res_ov.status_code == 200
    assert res_ov.json()["total_students"] >= 1

    # Branches
    res_br = client.get("/api/v1/admin/analytics/branches", headers=headers)
    assert res_br.status_code == 200
    assert isinstance(res_br.json(), list)

    # Internships
    res_in = client.get("/api/v1/admin/analytics/internships", headers=headers)
    assert res_in.status_code == 200
    assert "by_category" in res_in.json()

    # Organizations
    res_org = client.get("/api/v1/admin/analytics/organizations", headers=headers)
    assert res_org.status_code == 200
    assert isinstance(res_org.json(), list)

def test_phase3_photo_upload_replacement_and_security():
    admin_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    headers = {"Authorization": f"Bearer {admin_res.json()['access_token']}"}

    # 1. Upload first passport photo
    fake_img1 = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00fakejpg1")
    upload1 = client.post(
        "/api/v1/documents/student/21A91A0501/upload",
        headers=headers,
        data={"doc_type": "photo"},
        files={"file": ("photo1.jpg", fake_img1.getvalue(), "image/jpeg")}
    )
    assert upload1.status_code == 200
    path1 = upload1.json()["path"]

    # Verify student details returns latest photo
    st_res1 = client.get("/api/v1/admin/students/21A91A0501", headers=headers)
    assert st_res1.status_code == 200
    assert st_res1.json()["photo_image_path"] == path1

    # 2. Upload replacement (second) photo for same student
    fake_img2 = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00fakejpg2_updated")
    upload2 = client.post(
        "/api/v1/documents/student/21A91A0501/upload",
        headers=headers,
        data={"doc_type": "photo"},
        files={"file": ("photo2_updated.jpg", fake_img2.getvalue(), "image/jpeg")}
    )
    assert upload2.status_code == 200
    path2 = upload2.json()["path"]
    assert path2 != path1

    # Verify student details now returns the updated second photo immediately
    st_res2 = client.get("/api/v1/admin/students/21A91A0501", headers=headers)
    assert st_res2.status_code == 200
    assert st_res2.json()["photo_image_path"] == path2

    # 3. Verify public photo endpoint serves the updated photo
    pub_photo = client.get("/api/v1/public/photo/21A91A0501")
    assert pub_photo.status_code == 200
    assert pub_photo.headers.get("content-type") == "image/jpeg"

    # 4. Strict Aadhaar privacy check: direct view access to Aadhaar is forbidden
    view_aadhaar = client.get("/api/v1/documents/view?path=aadhaar/sample_aadhaar_card.jpg")
    assert view_aadhaar.status_code == 403

def test_phase3_dashboard_real_database_statistics():
    admin_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    headers = {"Authorization": f"Bearer {admin_res.json()['access_token']}"}

    # Fetch complete dashboard stats
    res = client.get("/api/v1/admin/dashboard-stats", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Category A: Student Statistics
    assert "total_students" in data
    assert data["total_students"] >= 1
    assert "branch_distribution" in data
    assert isinstance(data["branch_distribution"], dict)
    assert "gender_distribution" in data
    assert "admission_type_distribution" in data
    assert "completed_profiles" in data
    assert "incomplete_profiles" in data
    assert data["completed_profiles"] + data["incomplete_profiles"] == data["total_students"]

    # Category B: Internship Statistics
    assert "total_internships" in data
    assert "students_with_internships" in data
    assert "students_without_internships" in data
    assert data["students_with_internships"] + data["students_without_internships"] == data["total_students"]
    assert "organization_distribution" in data
    assert "district_distribution" in data
    assert "category_distribution" in data
    assert "mode_distribution" in data
    assert "certificates_received" in data
    assert "certificates_pending" in data

    # Category C: Academic Statistics
    assert "average_ug_cgpa" in data
    assert isinstance(data["average_ug_cgpa"], (int, float))
    assert "students_with_backlogs" in data
    assert "students_without_backlogs" in data
    assert data["students_with_backlogs"] + data["students_without_backlogs"] == data["total_students"]
    assert "year_distribution" in data
    assert "crt_registered_count" in data

    # Category D: System & Audit Statistics
    assert "total_admins" in data
    assert data["total_admins"] >= 1
    assert "total_clients" in data
    assert "approved_public_profiles" in data
    assert "pending_public_profiles" in data
    assert "recently_updated_students" in data
    assert isinstance(data["recently_updated_students"], list)

def test_reports_export_formats_and_authentication():
    # 1. Login to get token
    admin_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    assert admin_res.status_code == 200
    token = admin_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Excel export with Authorization header
    res_excel = client.get("/api/v1/reports/export?report_type=complete_student&format=excel", headers=headers)
    assert res_excel.status_code == 200
    assert "spreadsheetml" in res_excel.headers.get("content-type", "")
    assert len(res_excel.content) > 0

    # 3. Test CSV export with Authorization header
    res_csv = client.get("/api/v1/reports/export?report_type=academic&format=csv", headers=headers)
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers.get("content-type", "")
    assert len(res_csv.content) > 0

    # 4. Test PDF export with Authorization header
    res_pdf = client.get("/api/v1/reports/export?report_type=internship&format=pdf", headers=headers)
    assert res_pdf.status_code == 200
    assert "application/pdf" in res_pdf.headers.get("content-type", "")
    assert len(res_pdf.content) > 0

    # 5. Test export using ?token= query parameter (for direct links / window.open)
    res_token_param = client.get(f"/api/v1/reports/export?report_type=complete_student&format=excel&token={token}")
    assert res_token_param.status_code == 200
    assert "spreadsheetml" in res_token_param.headers.get("content-type", "")

    # 6. Test direct browser export URL without header (development fallback on localhost)
    res_dev = client.get("/api/v1/reports/export?report_type=complete_student&format=excel")
    assert res_dev.status_code == 200
    assert "spreadsheetml" in res_dev.headers.get("content-type", "")

    # 7. Test all valid report types generate without server error
    report_types = [
        "complete_student",
        "academic",
        "internship",
        "organization_wise",
        "crt_registered",
        "backlog",
        "without_internships",
        "certificate_pending"
    ]
    for r_type in report_types:
        r_res = client.get(f"/api/v1/reports/export?report_type={r_type}&format=csv", headers=headers)
        assert r_res.status_code == 200
        assert len(r_res.content) > 0


