import pytest
import io
import json
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.student import Student
from app.models.internship import Internship
from app.models.permissions import PublicProfilePermission
from app.models.audit import AuditLog
from app.utils.security import hash_password

client = TestClient(app)

@pytest.fixture(scope="module")
def admin_token():
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

# 1. Admin login
def test_workflow_01_admin_login():
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"})
    if res.status_code == 401:
        res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "SecurePassword2026!"})
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["user"]["role"] == "admin"

# 2. Client login
def test_workflow_02_client_login():
    res = client.post("/api/v1/auth/login", json={"username": "client", "password": "Client123!"})
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "client"

# 3. Password change
def test_workflow_03_password_change(client_token):
    headers = {"Authorization": f"Bearer {client_token}"}
    res = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"old_password": "Client123!", "new_password": "ClientNewPass123!"}
    )
    assert res.status_code == 200
    # Revert back
    revert_res = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"old_password": "ClientNewPass123!", "new_password": "Client123!"}
    )
    assert revert_res.status_code == 200

# 4. Student creation
def test_workflow_04_student_creation(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    student_payload = {
        "roll_no": "TEST_AUDIT_01",
        "full_name": "Audit Student Alpha",
        "branch": "Computer Science & Engineering",
        "branch_code": "CSE",
        "gender": "Female",
        "ug_cgpa": 8.75,
        "ug_year_of_pass": 2026,
        "no_of_backlogs": 0,
        "crt_registered": "Y",
        "aadhaar_number": "123456789012",
        "pan_number": "ABCDE1234F"
    }
    res = client.post("/api/v1/students", headers=headers, json=student_payload)
    if res.status_code == 400:
        assert "already exists" in res.json()["detail"]
    else:
        assert res.status_code == 201
        assert res.json()["roll_no"] == "TEST_AUDIT_01"

# 5. Student editing (Uses PUT /students/{roll_no})
def test_workflow_05_student_editing(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    update_res = client.put("/api/v1/students/TEST_AUDIT_01", headers=headers, json={"ug_cgpa": 9.1})
    assert update_res.status_code == 200
    assert update_res.json()["ug_cgpa"] == 9.1

# 6. Student deletion with safeguards (Uses DELETE /students/{roll_no})
def test_workflow_06_student_deletion(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Create temp student
    client.post("/api/v1/students", headers=headers, json={
        "roll_no": "TEST_TEMP_DEL",
        "full_name": "Temp Delete Student",
        "branch": "CSE"
    })
    del_res = client.delete("/api/v1/students/TEST_TEMP_DEL", headers=headers)
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.json()["message"]

    # Verify soft delete
    get_res = client.get("/api/v1/students/TEST_TEMP_DEL", headers=headers)
    assert get_res.status_code == 404

# 7. Student search by roll number
def test_workflow_07_search_by_roll_no(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/students?search=TEST_AUDIT_01", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] >= 1
    assert any(s["roll_no"] == "TEST_AUDIT_01" for s in res.json()["items"])

# 8. Student search by partial name
def test_workflow_08_search_by_partial_name(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/students?search=Audit Student", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] >= 1

# 9. Internship creation
def test_workflow_09_internship_creation(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "roll_no": "TEST_AUDIT_01",
        "full_name": "Audit Student Alpha",
        "branch": "CSE",
        "organization_name": "Acme Innovations Tech",
        "role": "Backend Intern",
        "mode": "Remote",
        "start_date": "2026-01-01",
        "end_date": "2026-03-31",
        "stipend_amount": 25000,
        "certificate_received": "Yes"
    }
    res = client.post("/api/v1/internships", headers=headers, json=payload)
    assert res.status_code == 201
    assert res.json()["organization_name"] == "Acme Innovations Tech"

# 10. Internship editing
def test_workflow_10_internship_editing(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    list_res = client.get("/api/v1/internships?roll_no=TEST_AUDIT_01", headers=headers)
    assert list_res.status_code == 200
    i_id = list_res.json()["items"][0]["id"]

    edit_res = client.put(f"/api/v1/internships/{i_id}", headers=headers, json={"role": "Lead Backend Intern"})
    assert edit_res.status_code == 200
    assert edit_res.json()["role"] == "Lead Backend Intern"

# 11. Internship deletion
def test_workflow_11_internship_deletion(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_res = client.post("/api/v1/internships", headers=headers, json={
        "roll_no": "TEST_AUDIT_01",
        "full_name": "Audit Student Alpha",
        "organization_name": "Temp Delete Corp"
    })
    i_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/internships/{i_id}", headers=headers)
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.json()["message"]

# 12. Excel student import
def test_workflow_12_excel_student_import(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    df = pd.DataFrame([{
        "Roll No.": "EXCEL_IMP_01",
        "Full Name (As per SSC)": "Excel Student One",
        "Branch": "CSE",
        "Branch Code": "CSE",
        "Gender": "Male",
        "UG/B.Tech CGPA": 8.0
    }])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    excel_bytes = buf.getvalue()
    files = {"file": ("student_import.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = client.post("/api/v1/imports/process", headers=headers, data={"template_type": "student"}, files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["total_records"] == 1
    assert data["inserted_count"] == 1 or data["updated_count"] == 1

# 13. Excel internship import
def test_workflow_13_excel_internship_import(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    df = pd.DataFrame([{
        "Roll No.": "EXCEL_IMP_01",
        "Name of the Organization": "Global Cloud Corp",
        "Role": "Cloud Engineer Intern",
        "Stipend Range": "15000-25000"
    }])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    excel_bytes = buf.getvalue()
    files = {"file": ("internship_import.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = client.post("/api/v1/imports/process", headers=headers, data={"template_type": "internship"}, files=files)
    assert res.status_code == 200
    assert res.json()["inserted_count"] >= 1 or res.json()["updated_count"] >= 1

# 14. Duplicate record handling
def test_workflow_14_duplicate_handling(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    df = pd.DataFrame([{
        "Roll No.": "EXCEL_IMP_01",
        "Full Name (As per SSC)": "Excel Student One Updated Name",
        "Branch": "CSE",
        "UG/B.Tech CGPA": 8.8
    }])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    files = {"file": ("student_dup.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = client.post("/api/v1/imports/process", headers=headers, data={"template_type": "student"}, files=files)
    assert res.status_code == 200
    assert res.json()["updated_count"] == 1

# 15. Blank-cell preservation
def test_workflow_15_blank_cell_preservation(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    s_before = client.get("/api/v1/students/EXCEL_IMP_01", headers=headers).json()
    assert s_before["branch"] == "CSE"

    df = pd.DataFrame([{
        "Roll No.": "EXCEL_IMP_01",
        "UG/B.Tech CGPA": 9.0
    }])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    files = {"file": ("blank_test.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    client.post("/api/v1/imports/process", headers=headers, data={"template_type": "student"}, files=files)

    s_after = client.get("/api/v1/students/EXCEL_IMP_01", headers=headers).json()
    assert s_after["ug_cgpa"] == 9.0
    assert s_after["branch"] == "CSE"

# 16. Failed-row reporting
def test_workflow_16_failed_row_reporting(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    df = pd.DataFrame([{
        "Roll No.": "",
        "Full Name (As per SSC)": "No Roll Student"
    }])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    files = {"file": ("fail_test.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = client.post("/api/v1/imports/process", headers=headers, data={"template_type": "student"}, files=files)
    assert res.status_code == 200
    assert res.json()["failed_count"] >= 1
    assert len(res.json()["failed_records"]) >= 1

# 17. PDF upload, 18. OCR extraction, 19. Manual correction
def test_workflow_17_18_19_pdf_flow(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, "STUDENT OFFER LETTER")
    c.drawString(100, 730, "Roll Number: TEST_PDF_01")
    c.drawString(100, 710, "Student Name: Jane Doe")
    c.drawString(100, 690, "Organization: FutureTech Solutions")
    c.drawString(100, 670, "Role: Machine Learning Intern")
    c.drawString(100, 650, "Monthly Stipend: Rs. 35000")
    c.drawString(100, 630, "Start Date: 2026-06-01")
    c.drawString(100, 610, "End Date: 2026-08-31")
    c.save()
    pdf_bytes = buf.getvalue()

    # 17 & 18: Upload and Extract
    files = {"file": ("offer_letter.pdf", pdf_bytes, "application/pdf")}
    res = client.post("/api/v1/pdf/extract", headers=headers, files=files)
    assert res.status_code == 200
    data = res.json()
    assert "history_id" in data
    h_id = data["history_id"]

    # 19: Manual correction and commit
    client.post("/api/v1/students", headers=headers, json={"roll_no": "TEST_PDF_01", "full_name": "Jane Doe", "branch": "CSE"})
    commit_res = client.post(
        f"/api/v1/pdf/commit/{h_id}",
        headers=headers,
        json={
            "roll_no": "TEST_PDF_01",
            "full_name": "Jane Doe Corrected",
            "organization_name": "FutureTech Solutions",
            "role": "Senior ML Intern",
            "branch": "CSE"
        }
    )
    assert commit_res.status_code == 200
    assert "Successfully updated" in commit_res.json()["message"]

# 20. Excel report generation
def test_workflow_20_excel_report(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/reports/export?report_type=complete_student&format=excel", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(res.content) > 100

# 21. CSV report generation
def test_workflow_21_csv_report(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/reports/export?report_type=academic&format=csv", headers=headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert b"Roll No" in res.content

# 22. PDF report generation
def test_workflow_22_pdf_report(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/reports/export?report_type=internship&format=pdf", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")

# 23. Public profile permissions
def test_workflow_23_public_profile_permissions(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Update public permission for student using /admin/permissions/{roll_no}
    perm_res = client.put(
        "/api/v1/admin/permissions/TEST_AUDIT_01",
        headers=headers,
        json={
            "is_public_approved": True,
            "student_consent_given": True,
            "publish_cgpa": True,
            "publish_gender": False,
            "publish_internships": True
        }
    )
    assert perm_res.status_code == 200
    assert "Updated public permission" in perm_res.json()["message"]

    # Test public endpoint access
    pub_res = client.get("/api/v1/public/profile/TEST_AUDIT_01")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    assert pub_data["roll_no"] == "TEST_AUDIT_01"
    assert pub_data["ug_cgpa"] == 9.1
    assert pub_data["gender"] is None
    assert "aadhaar_number" not in pub_data

# 24. Admin client account management
def test_workflow_24_admin_client_account_mgmt(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/admin/clients", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    new_client_payload = {
        "username": "test_auditor_client_2",
        "email": "auditor_client_2@test.edu",
        "full_name": "Audit Client User 2",
        "password": "TemporaryPassword123!"
    }
    create_res = client.post("/api/v1/admin/clients", headers=headers, json=new_client_payload)
    if create_res.status_code == 400:
        assert "already exists" in create_res.json()["detail"]
    else:
        assert create_res.status_code == 201

# 25. Audit log generation
def test_workflow_25_audit_log_generation(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/admin/audit-logs?page_size=10", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert "action" in data["items"][0]
    assert "username" in data["items"][0]
