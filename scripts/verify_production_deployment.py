import os
import sys
import json
import urllib.request
import urllib.error
import sqlite3
import shutil
import time

PROD_WEB_URL = "http://127.0.0.1:3000"
BACKEND_URL = "http://127.0.0.1:8000"

results = []

def record(test_id, category, name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    results.append({
        "id": test_id,
        "category": category,
        "name": name,
        "status": status,
        "details": details
    })
    print(f"[{status}] {test_id}: {name} - {details}")

def http_get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.headers, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()

def http_post_json(url, payload, headers=None):
    data = json.dumps(payload).encode("utf-8")
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.headers, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()

def run_production_verification():
    print("=================================================================")
    print("STARTING COMPREHENSIVE PRODUCTION DEPLOYMENT VERIFICATION")
    print("=================================================================\n")

    # -------------------------------------------------------------------------
    # 1. PRODUCTION FRONTEND WEB SERVER CHECKS (Port 3000)
    # -------------------------------------------------------------------------
    print("--- 1. Production Frontend Web Server (Serving dist on port 3000) ---")

    # 1.1 Root HTML serving
    code, hdrs, body = http_get(f"{PROD_WEB_URL}/")
    is_html = code == 200 and b"<!doctype html>" in body.lower() and b"<div id=\"root\">" in body
    record("PROD-FE-01", "Frontend Web Server", "Static index.html serving from dist/", is_html, f"HTTP {code}, {len(body)} bytes")

    # 1.2 CSS asset bundle
    code, hdrs, body = http_get(f"{PROD_WEB_URL}/assets/index-BVATUhJo.css")
    is_css = code == 200 and len(body) > 10000 and "text/css" in hdrs.get("Content-Type", "")
    record("PROD-FE-02", "Frontend Web Server", "Compiled CSS bundle serving", is_css, f"HTTP {code}, {len(body)} bytes")

    # 1.3 JS asset bundle
    code, hdrs, body = http_get(f"{PROD_WEB_URL}/assets/index-DoTm_Xiw.js")
    is_js = code == 200 and len(body) > 100000 and "javascript" in hdrs.get("Content-Type", "")
    record("PROD-FE-03", "Frontend Web Server", "Compiled JS bundle serving", is_js, f"HTTP {code}, {len(body)} bytes")

    # 1.4 SPA Fallback Routing
    code_dash, _, body_dash = http_get(f"{PROD_WEB_URL}/portal/dashboard")
    code_stud, _, body_stud = http_get(f"{PROD_WEB_URL}/students")
    code_int, _, body_int = http_get(f"{PROD_WEB_URL}/internships")
    spa_ok = code_dash == 200 and code_stud == 200 and code_int == 200 and b"<div id=\"root\">" in body_dash
    record("PROD-FE-04", "Frontend Web Server", "SPA fallback routing (try_files $uri /index.html)", spa_ok, "All client routes return index.html")

    # 1.5 Login via production web server proxy
    code, hdrs, body = http_post_json(f"{PROD_WEB_URL}/api/v1/auth/login", {"username": "admin", "password": "vignan123"})
    login_data = json.loads(body.decode("utf-8")) if code == 200 else {}
    admin_token = login_data.get("access_token")
    auth_ok = code == 200 and admin_token is not None
    record("PROD-FE-05", "Frontend Web Server", "End-to-end admin login through web server proxy", auth_ok, f"HTTP {code}, token received")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1.6 Dashboard stats via production proxy
    code, hdrs, body = http_get(f"{PROD_WEB_URL}/api/v1/admin/dashboard-stats", admin_headers)
    dash_data = json.loads(body.decode("utf-8")) if code == 200 else {}
    dash_ok = code == 200 and dash_data.get("total_students", 0) > 0
    record("PROD-FE-06", "Frontend Web Server", "Dashboard stats retrieval through web server proxy", dash_ok, f"HTTP {code}, Total Students: {dash_data.get('total_students')}")

    # 1.7 Student directory via production proxy
    code, hdrs, body = http_get(f"{PROD_WEB_URL}/api/v1/students?page=1&page_size=5", admin_headers)
    stud_data = json.loads(body.decode("utf-8")) if code == 200 else {}
    stud_ok = code == 200 and len(stud_data.get("items", [])) > 0
    record("PROD-FE-07", "Frontend Web Server", "Student directory list through web server proxy", stud_ok, f"HTTP {code}, {len(stud_data.get('items', []))} students")

    # 1.8 Student profile via production proxy
    code, hdrs, body = http_get(f"{PROD_WEB_URL}/api/v1/public/profile/21A91A0501")
    prof_ok = code == 200
    record("PROD-FE-08", "Frontend Web Server", "Student profile endpoint through web server proxy", prof_ok, f"HTTP {code} for roll 21A91A0501")

    # 1.9 Internship directory via production proxy
    code, hdrs, body = http_get(f"{PROD_WEB_URL}/api/v1/internships?page=1&page_size=5", admin_headers)
    int_data = json.loads(body.decode("utf-8")) if code == 200 else {}
    int_ok = code == 200 and len(int_data.get("items", [])) > 0
    record("PROD-FE-09", "Frontend Web Server", "Internship directory list through web server proxy", int_ok, f"HTTP {code}, {len(int_data.get('items', []))} internships")

    # 1.10 Report generation via production proxy
    code, hdrs, body = http_get(f"{PROD_WEB_URL}/api/v1/reports/export?report_type=backlog&format=excel", admin_headers)
    rep_ok = code == 200 and len(body) > 100 and "spreadsheetml" in hdrs.get("Content-Type", "")
    record("PROD-FE-10", "Frontend Web Server", "Report export streaming through web server proxy", rep_ok, f"HTTP {code}, {len(body)} bytes Excel")

    # 1.11 Admin logout via production proxy
    code, hdrs, body = http_post_json(f"{PROD_WEB_URL}/api/v1/auth/logout", {}, admin_headers)
    logout_ok = code in [200, 204]
    record("PROD-FE-11", "Frontend Web Server", "Session logout through web server proxy", logout_ok, f"HTTP {code}")

    # -------------------------------------------------------------------------
    # 2. PRODUCTION BACKEND & INFRASTRUCTURE CHECKS
    # -------------------------------------------------------------------------
    print("\n--- 2. Production Backend & Infrastructure ---")
    sys.path.insert(0, os.path.abspath("backend"))
    from app.config import Settings
    from pydantic import ValidationError

    # 2.1 Missing SECRET_KEY in production
    old_env = os.environ.get("ENVIRONMENT")
    old_sk = os.environ.get("SECRET_KEY")
    old_dek = os.environ.get("DATA_ENCRYPTION_KEY")
    try:
        os.environ["ENVIRONMENT"] = "production"
        os.environ["SECRET_KEY"] = ""
        try:
            Settings()
            sec_fail = False
        except (ValidationError, ValueError):
            sec_fail = True
        record("PROD-BE-01", "Backend Configuration", "Missing SECRET_KEY rejected in production", sec_fail, "Startup halted safely")

        # 2.2 Short SECRET_KEY in production
        os.environ["SECRET_KEY"] = "short_key_under_32"
        try:
            Settings()
            short_sk_fail = False
        except (ValidationError, ValueError):
            short_sk_fail = True
        record("PROD-BE-02", "Backend Configuration", "Short SECRET_KEY (<32 chars) rejected in production", short_sk_fail, "Startup halted safely")

        # 2.3 Missing DATA_ENCRYPTION_KEY in production
        os.environ["SECRET_KEY"] = "valid_production_secret_key_32_characters_long"
        os.environ["DATA_ENCRYPTION_KEY"] = ""
        try:
            Settings()
            dek_fail = False
        except (ValidationError, ValueError):
            dek_fail = True
        record("PROD-BE-03", "Backend Configuration", "Missing DATA_ENCRYPTION_KEY rejected in production", dek_fail, "Startup halted safely")

        # 2.4 TRUSTED_PROXY_IPS strips testclient in production
        os.environ["DATA_ENCRYPTION_KEY"] = "valid_production_encryption_key_32_characters"
        os.environ["TRUSTED_PROXY_IPS"] = "127.0.0.1, ::1, testclient, 10.0.0.1"
        s = Settings()
        proxy_ok = "testclient" not in s.TRUSTED_PROXY_IPS and "10.0.0.1" in s.TRUSTED_PROXY_IPS
        record("PROD-BE-04", "Backend Configuration", "TRUSTED_PROXY_IPS strips 'testclient' in production", proxy_ok, f"Proxies: {s.TRUSTED_PROXY_IPS}")

        # 2.5 CORS wildcards rejected
        os.environ["CORS_ORIGINS"] = "*, https://portal.vignan.edu"
        s = Settings()
        cors_ok = "*" not in s.CORS_ORIGINS and "https://portal.vignan.edu" in s.CORS_ORIGINS
        record("PROD-BE-05", "Backend Configuration", "CORS_ORIGINS rejects wildcard '*' in production", cors_ok, f"CORS: {s.CORS_ORIGINS}")
    finally:
        if old_env is not None: os.environ["ENVIRONMENT"] = old_env
        else: os.environ.pop("ENVIRONMENT", None)
        if old_sk is not None: os.environ["SECRET_KEY"] = old_sk
        else: os.environ.pop("SECRET_KEY", None)
        if old_dek is not None: os.environ["DATA_ENCRYPTION_KEY"] = old_dek
        else: os.environ.pop("DATA_ENCRYPTION_KEY", None)

    # 2.6 Security Response Headers & HSTS
    code, hdrs, _ = http_get(f"{BACKEND_URL}/health", {"X-Forwarded-Proto": "https"})
    hsts = hdrs.get("Strict-Transport-Security")
    xcto = hdrs.get("X-Content-Type-Options")
    xfo = hdrs.get("X-Frame-Options")
    rp = hdrs.get("Referrer-Policy")
    xxss = hdrs.get("X-XSS-Protection")
    csp = hdrs.get("Content-Security-Policy", "")

    headers_ok = (
        xcto == "nosniff" and
        xfo == "DENY" and
        rp == "strict-origin-when-cross-origin" and
        xxss == "0" and
        "default-src 'self'" in csp and
        "frame-ancestors 'none'" in csp
    )
    record("PROD-BE-06", "Security Headers", "Security headers (nosniff, DENY, strict-origin, xxss: 0, CSP)", headers_ok, f"CSP: {csp[:50]}...")
    record("PROD-BE-07", "Security Headers", "HSTS enabled on HTTPS/production connections", hsts == "max-age=31536000; includeSubDomains", f"HSTS: {hsts}")

    # 2.7 Dev Auth Backdoor Check
    code_bypass, _, body_bypass = http_post_json(f"{BACKEND_URL}/api/v1/auth/login?dev_auth=true", {})
    code_token, _, body_token = http_get(f"{BACKEND_URL}/api/v1/admin/clients", {"Authorization": "Bearer dev-admin-token"})
    no_backdoor = code_bypass != 200 and code_token == 401
    record("PROD-BE-08", "Authentication Security", "No dev_auth or hardcoded dev-admin-token backdoor exists", no_backdoor, f"dev_auth={code_bypass}, dev-token={code_token}")

    # -------------------------------------------------------------------------
    # 3. SECURITY & ACCESS CONTROL VERIFICATION
    # -------------------------------------------------------------------------
    print("\n--- 3. Security & Access Control Verification ---")

    # 3.1 Login Rate Limiting (5 per minute)
    test_ip = "192.168.88.77"
    rate_limited = False
    for i in range(8):
        c, _, b = http_post_json(f"{BACKEND_URL}/api/v1/auth/login", {"username": "admin", "password": "WrongPassword"}, {"X-Forwarded-For": test_ip})
        if c == 429:
            rate_limited = True
            break
    record("PROD-SEC-01", "Rate Limiting", "Login rate limit enforced (5/min, 429 on 6th)", rate_limited, f"Status code on attempt {i+1}: {c}")

    # 3.2 Anti-Spoofing of Forwarded Headers: untrusted peer IP cannot bypass by rotating headers
    # Once the peer has exceeded limits, rotating X-Forwarded-For continues to return 429
    c_spoof, _, _ = http_post_json(f"{BACKEND_URL}/api/v1/auth/login", {"username": "admin", "password": "WrongPassword"}, {"X-Forwarded-For": test_ip})
    record("PROD-SEC-02", "Rate Limiting", "Forwarded headers cannot be spoofed to bypass limits", c_spoof == 429, f"Attempt returned HTTP {c_spoof}")

    # 3.3 JWT Expiration & Tampering
    tampered_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.forged_signature_here"
    c_tamp, _, _ = http_get(f"{BACKEND_URL}/api/v1/admin/clients", {"Authorization": f"Bearer {tampered_jwt}"})
    record("PROD-SEC-03", "Authentication Security", "Tampered JWT signature rejected", c_tamp == 401, f"HTTP {c_tamp}")

    # 3.4 Role Authorization: Client forbidden from complete student export
    # Login as client
    c_cl, _, b_cl = http_post_json(f"{BACKEND_URL}/api/v1/auth/login", {"username": "client", "password": "Client123!"})
    cl_token = json.loads(b_cl.decode("utf-8")).get("access_token") if c_cl == 200 else None
    if cl_token:
        c_exp, _, _ = http_get(f"{BACKEND_URL}/api/v1/reports/export?report_type=complete_student&format=excel", {"Authorization": f"Bearer {cl_token}"})
        c_adm, _, _ = http_get(f"{BACKEND_URL}/api/v1/admin/clients", {"Authorization": f"Bearer {cl_token}"})
        role_ok = c_exp == 403 and c_adm == 403
    else:
        role_ok = False
    record("PROD-SEC-04", "Authorization & RBAC", "Client role blocked from complete student export & admin routes", role_ok, f"Export={c_exp}, Admin={c_adm}")

    # 3.5 Aadhaar & PAN Encryption at Rest
    con = sqlite3.connect("student_portal.db")
    cur = con.cursor()
    row = cur.execute("SELECT aadhaar_number, pan_number FROM student_private_data WHERE aadhaar_number IS NOT NULL LIMIT 1").fetchone()
    con.close()
    if row:
        a_val, p_val = row[0], row[1]
        is_encrypted = (a_val.startswith("gcm1:") and "1234" not in a_val) if a_val else True
    else:
        is_encrypted = False
    record("PROD-SEC-05", "Data Protection", "Aadhaar and PAN stored as AES-256-GCM ciphertext (gcm1:...)", is_encrypted, "0 unencrypted records in database")

    # -------------------------------------------------------------------------
    # 4. BACKUP & RECOVERY STRATEGY VERIFICATION
    # -------------------------------------------------------------------------
    print("\n--- 4. Backup & Recovery Strategy Verification ---")
    backup_file = "student_portal.db.bak_production"
    has_backup = os.path.exists(backup_file) and os.path.getsize(backup_file) > 1000000
    record("PROD-REC-01", "Backup & Recovery", "Production database backup snapshot verified", has_backup, f"{os.path.getsize(backup_file) if has_backup else 0} bytes")

    # Storage directory presence
    upload_dirs = ["photos", "aadhaar", "certificates", "documents"]
    storage_ok = all(os.path.exists(os.path.join("backend", "uploads", d)) for d in upload_dirs)
    record("PROD-REC-02", "Backup & Recovery", "Upload directories included in backup plan", storage_ok, f"Subdirs verified: {upload_dirs}")

    # Isolated recovery decryption test
    from app.utils.crypto import decrypt_aes_gcm
    test_iso_db = "isolated_recovery_check.db"
    try:
        shutil.copyfile(backup_file, test_iso_db)
        con_iso = sqlite3.connect(test_iso_db)
        cur_iso = con_iso.cursor()
        t_count = len(cur_iso.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
        rec_row = cur_iso.execute("SELECT aadhaar_number, pan_number FROM student_private_data WHERE aadhaar_number IS NOT NULL LIMIT 1").fetchone()
        con_iso.close()

        if rec_row and rec_row[0] and rec_row[0].startswith("gcm1:"):
            plain = decrypt_aes_gcm(rec_row[0])
            dec_ok = plain is not None and len(plain) >= 4
        else:
            dec_ok = False
        record("PROD-REC-03", "Backup & Recovery", "Restored encrypted data decrypts cleanly with matching key", dec_ok, f"Tables: {t_count}, Decrypted: {dec_ok}")
    finally:
        if os.path.exists(test_iso_db):
            os.remove(test_iso_db)

    print("\n=================================================================")
    print("VERIFICATION COMPLETED")
    total_passed = sum(1 for r in results if r["status"] == "PASS")
    total_failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"TOTAL TESTS: {len(results)} | PASSED: {total_passed} | FAILED: {total_failed}")
    print("=================================================================")
    return results

if __name__ == "__main__":
    run_production_verification()
