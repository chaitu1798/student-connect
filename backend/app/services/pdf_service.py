import io
import re
import json
from pypdf import PdfReader
from PIL import Image
from sqlalchemy.orm import Session
from app.models.student import Student, StudentContact, StudentAcademic
from app.models.history import PdfUploadHistory

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

ROLL_PATTERNS = [
    r"\b\d{2}[A-Za-z0-9]{2}[15][A-Za-z0-9]{5}\b",  # e.g. 21A91A0501, 20B91A1204
    r"\b[A-Za-z]{2,4}\d{4,8}\b",
    r"(?:Roll\s*(?:No|Number)?|HT\s*No|Hall\s*Ticket)[:\s-]*([A-Za-z0-9]+)",
]

EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_PATTERN = r"(?:\+91[- ]?)?[6-9]\d{9}"
CGPA_PATTERN = r"(?:CGPA|Percentage)[:\s]*([0-9]+(?:\.[0-9]+)?)"
BRANCH_PATTERNS = [
    r"\b(Computer Science(?: and Engineering)?|CSE)\b",
    r"\b(Information Technology|IT)\b",
    r"\b(Electronics and Communication(?: Engineering)?|ECE)\b",
    r"\b(Electrical and Electronics(?: Engineering)?|EEE)\b",
    r"\b(Mechanical Engineering|MECH)\b",
    r"\b(Civil Engineering|CIVIL)\b",
    r"\b(Data Science|AI|Artificial Intelligence)\b",
]

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract readable text using pypdf, with OCR fallback if empty."""
    text = ""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"PDF text extraction error: {e}")

    # Fallback OCR if text is essentially empty (scanned PDF)
    if len(text.strip()) < 20 and PYTESSERACT_AVAILABLE:
        try:
            # We can extract images from pages if any
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                for img_obj in page.images:
                    img = Image.open(io.BytesIO(img_obj.data))
                    ocr_text = pytesseract.image_to_string(img)
                    text += ocr_text + "\n"
        except Exception as ocr_err:
            print(f"OCR extraction error: {ocr_err}")

    return text

def parse_student_details_from_text(text: str) -> dict:
    details = {
        "roll_no": None,
        "full_name": None,
        "email": None,
        "contact_no": None,
        "branch": None,
        "cgpa": None,
        "year_of_pass": None,
        "raw_text_snippet": text[:500] if text else "",
    }

    if not text:
        return details

    # 1. Roll No
    for pattern in ROLL_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            details["roll_no"] = (match.group(1) if match.groups() else match.group(0)).strip().upper()
            break

    # 2. Email
    email_match = re.search(EMAIL_PATTERN, text)
    if email_match:
        details["email"] = email_match.group(0).strip()

    # 3. Phone
    phone_match = re.search(PHONE_PATTERN, text)
    if phone_match:
        details["contact_no"] = phone_match.group(0).strip()

    # 4. CGPA
    cgpa_match = re.search(CGPA_PATTERN, text, re.IGNORECASE)
    if cgpa_match:
        try:
            cgpa_val = float(cgpa_match.group(1))
            if cgpa_val <= 10.0:
                details["cgpa"] = cgpa_val
            elif cgpa_val <= 100.0:
                details["cgpa"] = round(cgpa_val / 9.5, 2)
        except ValueError:
            pass

    # 5. Branch
    for b_pat in BRANCH_PATTERNS:
        b_match = re.search(b_pat, text, re.IGNORECASE)
        if b_match:
            details["branch"] = b_match.group(0).strip()
            break

    # 6. Name extraction heuristic (e.g. Name: <John Doe>)
    name_match = re.search(r"(?:Name|Student\s*Name|Candidate\s*Name)[:\s-]*([A-Za-z\s.]{3,40})", text, re.IGNORECASE)
    if name_match:
        details["full_name"] = name_match.group(1).strip()

    # 7. Passing year
    year_match = re.search(r"\b(20[12]\d)\b", text)
    if year_match:
        details["year_of_pass"] = int(year_match.group(1))

    return details

def process_pdf_upload(
    db: Session,
    file_bytes: bytes,
    filename: str,
    user_id: int | None
) -> dict:
    raw_text = extract_text_from_pdf(file_bytes)
    extracted = parse_student_details_from_text(raw_text)

    matched_roll = extracted.get("roll_no")
    existing_student_info = None

    if matched_roll:
        student = db.query(Student).filter(Student.roll_no == matched_roll).first()
        if student:
            existing_student_info = {
                "id": student.id,
                "roll_no": student.roll_no,
                "full_name": student.full_name,
                "branch": student.branch,
                "ug_cgpa": student.academics.ug_cgpa if student.academics else None,
                "contact_no": student.contacts.contact_number if student.contacts else None,
            }

    history = PdfUploadHistory(
        file_name=filename,
        extracted_data_json=json.dumps(extracted),
        matched_roll_no=matched_roll,
        status="extracted",
        uploaded_by_user_id=user_id,
    )
    db.add(history)
    db.commit()

    return {
        "history_id": history.id,
        "file_name": filename,
        "extracted_data": extracted,
        "matched_existing_student": existing_student_info,
        "raw_text": raw_text[:2000],
    }

def commit_pdf_extracted_data(
    db: Session,
    history_id: int,
    reviewed_data: dict,
    user_id: int | None
) -> dict:
    history = db.query(PdfUploadHistory).filter(PdfUploadHistory.id == history_id).first()
    if not history:
        raise ValueError("Upload record not found")

    roll_no = reviewed_data.get("roll_no")
    if not roll_no:
        raise ValueError("Roll Number is required to save data")

    student = db.query(Student).filter(Student.roll_no == roll_no).first()
    if not student:
        student = Student(
            roll_no=roll_no,
            full_name=reviewed_data.get("full_name") or roll_no,
            branch=reviewed_data.get("branch"),
            created_by_user_id=user_id,
        )
        db.add(student)
        db.flush()

        contacts = StudentContact(
            student_id=student.id,
            recorded_email=reviewed_data.get("email"),
            contact_number=reviewed_data.get("contact_no"),
        )
        db.add(contacts)

        academics = StudentAcademic(
            student_id=student.id,
            ug_cgpa=reviewed_data.get("cgpa"),
            ug_year_of_passing=reviewed_data.get("year_of_pass"),
        )
        db.add(academics)
    else:
        # Update existing without overwriting blanks
        if reviewed_data.get("full_name"):
            student.full_name = reviewed_data["full_name"]
        if reviewed_data.get("branch"):
            student.branch = reviewed_data["branch"]

        if not student.contacts:
            student.contacts = StudentContact(student_id=student.id)
            db.add(student.contacts)
        if reviewed_data.get("email"):
            student.contacts.recorded_email = reviewed_data["email"]
        if reviewed_data.get("contact_no"):
            student.contacts.contact_number = reviewed_data["contact_no"]

        if not student.academics:
            student.academics = StudentAcademic(student_id=student.id)
            db.add(student.academics)
        if reviewed_data.get("cgpa"):
            student.academics.ug_cgpa = reviewed_data["cgpa"]
        if reviewed_data.get("year_of_pass"):
            student.academics.ug_year_of_passing = reviewed_data["year_of_pass"]

        student.updated_by_user_id = user_id

    history.status = "committed"
    db.commit()

    return {"message": f"Successfully updated student record for Roll No: {roll_no}"}
