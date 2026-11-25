import io
import json
import math
from datetime import datetime, date
import pandas as pd
from sqlalchemy.orm import Session
from app.models.student import (
    Student,
    StudentAcademic,
    StudentContact,
    StudentPrivateData,
    StudentAddress,
    StudentPublicationSetting,
    StudentConsent,
)
from app.models.internship import Internship
from app.models.history import ExcelImportHistory

STUDENT_FIELD_SYNONYMS = {
    "s_no": ["s.no", "s.no.", "sno", "serial no", "serial number", "sl no"],
    "recorded_email": ["email address (recorded)", "recorded email", "email address", "email", "recorded email id"],
    "roll_no": ["roll no", "roll no.", "roll number", "rollno", "ht no", "hall ticket no", "registration no"],
    "full_name": ["full name (as per ssc)", "full name", "student name", "name as per ssc", "name"],
    "column1": ["column1", "column 1", "remarks", "notes"],
    "branch": ["branch", "department", "stream", "course"],
    "branch_code": ["branch code", "dept code", "branch_code"],
    "gender": ["gender", "sex"],
    "contact_no": ["contact no", "contact no.", "phone", "student mobile", "mobile no", "mobile"],
    "parent_contact_no": ["parent contact no", "parent contact no.", "parent mobile", "father mobile", "parent contact"],
    "corrected_placements_email": ["corrected placements email id", "placements email", "placement email id", "placement email"],
    "alternate_personal_email": ["alternate personal email id", "alternate email", "personal email", "personal email id"],
    "ug_cgpa": ["ug/b.tech cgpa", "ug cgpa", "b.tech cgpa", "cgpa", "btech cgpa"],
    "ug_year_of_pass": ["ug year of pass", "year of pass", "passing year", "ug passing year", "yop"],
    "no_of_backlogs": ["no. of backlogs", "backlogs", "no of backlogs", "standing backlogs"],
    "first_name": ["first name", "firstname"],
    "middle_name": ["middle name", "middlename"],
    "last_name": ["last name", "lastname", "surname"],
    "date_of_birth": ["date of birth", "dob", "birth date"],
    "crt_registered": ["crt registered (y/n)", "crt registered", "crt", "crt registration"],
    "x_grading_system": ["xth grading system", "10th grading system", "ssc grading system"],
    "x_cgpa_percentage": ["enter xth cgpa/percentage", "xth cgpa", "xth percentage", "10th cgpa", "10th percentage", "ssc marks"],
    "x_year_of_pass": ["grade x year of pass", "10th year of pass", "ssc year of pass"],
    "x_school_name": ["name of the school", "school name", "10th school name", "ssc school"],
    "study_after_x": ["study after xth", "study after 10th", "intermediate or diploma"],
    "xii_grading_system": ["xiith/diploma grading system", "12th grading system", "diploma grading system", "inter grading system"],
    "xii_percentage_cgpa": ["enter xiith/diploma percentage/cgpa", "12th percentage", "inter percentage", "diploma percentage", "xiith cgpa"],
    "xii_year_of_pass": ["grade xiith/diploma year of pass", "12th year of pass", "inter year of pass", "diploma year of pass"],
    "xii_college_name": ["xiith/diploma college name", "junior college name", "diploma college name", "12th college name"],
    "admission_type": ["admission type", "type of admission", "quota"],
    "entrance_exam": ["entrance exam taken for admission", "entrance exam", "exam taken"],
    "entrance_rank": ["eapcet/e-cet rank", "eapcet rank", "ecet rank", "entrance rank", "rank"],
    "father_name": ["father name", "father's name", "parent name"],
    "father_occupation": ["father occupation", "father's occupation", "parent occupation"],
    "languages_known": ["languages known", "languages"],
    "caste": ["caste", "category/caste", "social category"],
    "residential_address": ["full residential address", "residential address", "address", "permanent address"],
    "pan_number": ["pan card number", "pan number", "pan", "pan no"],
    "aadhaar_number": ["aadhaar number", "aadhaar card number", "aadhaar", "aadhaar no", "aadhar number", "aadhar"],
}

INTERNSHIP_FIELD_SYNONYMS = {
    "s_no": ["s.no", "s.no.", "sno", "sl no"],
    "roll_no": ["roll no", "roll no.", "roll number", "rollno", "ht no", "hall ticket no"],
    "full_name": ["full name (as per ssc)", "full name", "student name", "name as per ssc"],
    "branch": ["branch", "department", "stream"],
    "college_name": ["name of college", "college name", "college"],
    "organization_name": ["name of organization (internship)", "organization name", "company name", "organization", "company"],
    "organization_district": ["organization district", "district", "company location district"],
    "category": ["category", "internship domain", "domain"],
    "role": ["role", "designation", "job role", "internship role"],
    "mode": ["mode of internship", "mode", "internship mode", "work mode"],
    "internship_type": ["internship type", "type", "paid/unpaid"],
    "stipend_amount": ["stipend (₹/month)", "stipend", "stipend per month", "monthly stipend", "stipend amount"],
    "start_date": ["start date", "from date", "commencement date", "joining date"],
    "end_date": ["end date", "to date", "completion date"],
    "certificate_received": ["certificate received", "certificate status", "certificate submitted"],
    "duration_weeks": ["duration (weeks)", "duration in weeks", "duration", "duration (in weeks)"],
    "organization_address": ["address of organization", "company address", "organization address"],
    "stipend_range": ["stipend range", "salary range"],
    "offered_by": ["internship offered by", "offered by", "platform/offered by"],
    "regular_internship": ["regular internship (aep / idea lab)", "regular internship", "internship category type"],
    "gender": ["gender", "sex"],
    "contact_no": ["contact no", "contact no.", "student contact", "phone"],
}

def clean_val(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    val_str = str(val).strip()
    if val_str == "" or val_str.lower() in ["nan", "none", "null", "n/a", "na"]:
        return None
    return val_str

def parse_date(val):
    if not val:
        return None
    if isinstance(val, (datetime, date)):
        return val.date() if isinstance(val, datetime) else val
    val_str = str(val).strip()
    formats = [
        "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y",
        "%d.%m.%Y", "%Y/%m/%d", "%d %b %Y", "%d %B %Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            pass
    return None

def calculate_duration_weeks(start_date: date | None, end_date: date | None) -> int | None:
    if not start_date or not end_date:
        return None
    days = (end_date - start_date).days
    if days < 0:
        return 0
    return max(1, round(days / 7))

def map_headers(columns: list[str], template_type: str) -> dict[str, str]:
    """Map detected dataframe columns to standard model fields."""
    synonyms = STUDENT_FIELD_SYNONYMS if template_type == "student" else INTERNSHIP_FIELD_SYNONYMS
    mapping = {}
    for col in columns:
        col_clean = str(col).strip().lower()
        matched_field = None
        for field, alt_names in synonyms.items():
            if col_clean == field or col_clean in alt_names:
                matched_field = field
                break
        if matched_field:
            mapping[col] = matched_field
    return mapping

def read_excel_or_csv(file_bytes: bytes, filename: str) -> pd.DataFrame:
    from app.utils.security import verify_file_signature
    if not verify_file_signature(file_bytes, filename):
        raise ValueError("Invalid file signature or corrupted/disguised spreadsheet file")

    fn = filename.lower()
    if fn.endswith(".csv"):
        return pd.read_csv(io.BytesIO(file_bytes))
    elif fn.endswith(".xls"):
        return pd.read_excel(io.BytesIO(file_bytes), engine="xlrd")
    else:  # .xlsx or fallback
        return pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")

def preview_import(file_bytes: bytes, filename: str, template_type: str, custom_mapping: dict | None = None) -> dict:
    df = read_excel_or_csv(file_bytes, filename)
    cols = [str(c) for c in df.columns]
    mapping = custom_mapping or map_headers(cols, template_type)

    preview_rows = []
    seen_roll_numbers = set()
    duplicate_sheet_rolls = set()

    for idx, row in df.head(10).iterrows():
        row_dict = {}
        for orig_col, field_key in mapping.items():
            if orig_col in row:
                row_dict[field_key] = clean_val(row[orig_col])
        preview_rows.append(row_dict)

    roll_col_orig = None
    for orig, field in mapping.items():
        if field == "roll_no":
            roll_col_orig = orig
            break

    total_rows = len(df)
    if roll_col_orig and roll_col_orig in df.columns:
        for val in df[roll_col_orig]:
            c_val = clean_val(val)
            if c_val:
                if c_val in seen_roll_numbers:
                    duplicate_sheet_rolls.add(c_val)
                seen_roll_numbers.add(c_val)

    return {
        "columns": cols,
        "mapping": mapping,
        "total_rows": total_rows,
        "preview_rows": preview_rows,
        "duplicate_in_sheet": list(duplicate_sheet_rolls),
        "roll_no_detected": bool(roll_col_orig),
    }

def process_student_import(
    db: Session,
    df: pd.DataFrame,
    mapping: dict,
    filename: str,
    user_id: int | None
) -> dict:
    inserted_count = 0
    updated_count = 0
    duplicate_count = 0
    failed_count = 0
    failed_records = []

    # Invert mapping to find field -> orig_col
    field_to_col = {v: k for k, v in mapping.items()}
    roll_col = field_to_col.get("roll_no")

    if not roll_col or roll_col not in df.columns:
        return {
            "error": "Mandatory column 'Roll No' not identified in template",
            "inserted_count": 0,
            "updated_count": 0,
            "duplicate_count": 0,
            "failed_count": len(df),
            "failed_records": [{"row": 0, "reason": "Missing Roll No column mapping"}],
        }

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-based index plus header row
        raw_roll = clean_val(row.get(roll_col))
        if not raw_roll:
            failed_count += 1
            failed_records.append({"row": row_num, "roll_no": "BLANK", "reason": "Roll No is required"})
            continue

        raw_name = clean_val(row.get(field_to_col.get("full_name", "")))
        
        # Check existing student in DB
        existing_student = db.query(Student).filter(Student.roll_no == raw_roll).first()

        row_data = {}
        for field, orig_c in field_to_col.items():
            if orig_c in row:
                val = clean_val(row[orig_c])
                if val is not None:
                    # Type casts
                    if field in ["ug_cgpa"]:
                        try:
                            row_data[field] = float(val)
                        except ValueError:
                            row_data[field] = None
                    elif field in ["ug_year_of_pass", "no_of_backlogs", "x_year_of_pass", "xii_year_of_pass"]:
                        try:
                            row_data[field] = int(float(val))
                        except ValueError:
                            row_data[field] = None
                    else:
                        row_data[field] = val

        try:
            # Map canonical academic/contact/private field names to model columns
            academic_model_map = {
                "ug_cgpa": "ug_cgpa",
                "ug_year_of_pass": "ug_year_of_passing",
                "no_of_backlogs": "number_of_backlogs",
                "crt_registered": "crt_registered",
                "x_grading_system": "x_grading_system",
                "x_cgpa_percentage": "x_cgpa_percentage",
                "x_year_of_pass": "x_year_of_passing",
                "x_school_name": "x_school_name",
                "study_after_x": "study_after_x",
                "xii_grading_system": "xii_grading_system",
                "xii_percentage_cgpa": "xii_cgpa_percentage",
                "xii_year_of_pass": "xii_year_of_passing",
                "xii_college_name": "xii_college_name",
                "admission_type": "admission_type",
                "entrance_exam": "entrance_exam",
                "entrance_rank": "entrance_rank",
            }
            contact_model_map = {
                "recorded_email": "recorded_email",
                "contact_no": "contact_number",
                "parent_contact_no": "parent_contact_number",
                "corrected_placements_email": "corrected_placement_email",
                "alternate_personal_email": "alternate_personal_email",
            }
            private_model_map = {
                "gender": "gender",
                "date_of_birth": "date_of_birth",
                "languages_known": "languages_known",
                "father_name": "father_name",
                "father_occupation": "father_occupation",
                "caste": "caste",
                "pan_number": "pan_number",
                "aadhaar_number": "aadhaar_number",
            }

            if existing_student:
                # Update existing student without overwriting with blank cells!
                for k, v in row_data.items():
                    if v is not None and hasattr(existing_student, k):
                        setattr(existing_student, k, v)
                existing_student.updated_by_user_id = user_id

                # Update or create related models
                if not existing_student.academics:
                    existing_student.academics = StudentAcademic(student_id=existing_student.id)
                for f, col in academic_model_map.items():
                    if f in row_data and row_data[f] is not None:
                        setattr(existing_student.academics, col, row_data[f])

                if not existing_student.contacts:
                    existing_student.contacts = StudentContact(student_id=existing_student.id)
                for f, col in contact_model_map.items():
                    if f in row_data and row_data[f] is not None:
                        setattr(existing_student.contacts, col, row_data[f])

                if not existing_student.private_data:
                    existing_student.private_data = StudentPrivateData(student_id=existing_student.id)
                for f, col in private_model_map.items():
                    if f in row_data and row_data[f] is not None:
                        setattr(existing_student.private_data, col, row_data[f])

                if "residential_address" in row_data and row_data["residential_address"]:
                    if not existing_student.addresses:
                        existing_student.addresses = StudentAddress(student_id=existing_student.id)
                    existing_student.addresses.full_residential_address = row_data["residential_address"]

                updated_count += 1
                duplicate_count += 1
            else:
                # Insert new student
                if not raw_name:
                    raw_name = raw_roll  # fallback if full name not present
                new_student = Student(
                    roll_no=raw_roll,
                    full_name=raw_name,
                    created_by_user_id=user_id,
                )
                for k, v in row_data.items():
                    if hasattr(new_student, k):
                        setattr(new_student, k, v)
                db.add(new_student)
                db.flush()

                # Add related models
                academics = StudentAcademic(student_id=new_student.id)
                for f, col in academic_model_map.items():
                    if f in row_data and row_data[f] is not None:
                        setattr(academics, col, row_data[f])
                db.add(academics)

                contacts = StudentContact(student_id=new_student.id)
                for f, col in contact_model_map.items():
                    if f in row_data and row_data[f] is not None:
                        setattr(contacts, col, row_data[f])
                db.add(contacts)

                private_data = StudentPrivateData(student_id=new_student.id)
                for f, col in private_model_map.items():
                    if f in row_data and row_data[f] is not None:
                        setattr(private_data, col, row_data[f])
                db.add(private_data)

                if "residential_address" in row_data and row_data["residential_address"]:
                    db.add(StudentAddress(student_id=new_student.id, full_residential_address=row_data["residential_address"]))

                pub = StudentPublicationSetting(
                    student_id=new_student.id,
                    is_public_approved=False,
                    publish_gender=False,
                    publish_cgpa=False,
                    publish_internships=True,
                )
                db.add(pub)
                db.add(StudentConsent(student_id=new_student.id, consent_given=True))

                inserted_count += 1

        except Exception as e:
            failed_count += 1
            failed_records.append({"row": row_num, "roll_no": raw_roll, "reason": str(e)})

    db.commit()

    # Record history
    history = ExcelImportHistory(
        file_name=filename,
        template_type="student",
        total_rows=len(df),
        inserted_count=inserted_count,
        updated_count=updated_count,
        duplicate_count=duplicate_count,
        failed_count=failed_count,
        failed_records_json=json.dumps(failed_records[:200]),
        status="completed" if failed_count == 0 else ("partial" if inserted_count + updated_count > 0 else "failed"),
        uploaded_by_user_id=user_id,
    )
    db.add(history)
    db.commit()

    return {
        "history_id": history.id,
        "template_type": "student",
        "total_records": len(df),
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "duplicate_count": duplicate_count,
        "failed_count": failed_count,
        "failed_records": failed_records,
        "message": f"Successfully processed {len(df)} records ({inserted_count} new, {updated_count} updated, {failed_count} failed).",
    }

def process_internship_import(
    db: Session,
    df: pd.DataFrame,
    mapping: dict,
    filename: str,
    user_id: int | None
) -> dict:
    inserted_count = 0
    updated_count = 0
    duplicate_count = 0
    failed_count = 0
    failed_records = []

    field_to_col = {v: k for k, v in mapping.items()}
    roll_col = field_to_col.get("roll_no")
    org_col = field_to_col.get("organization_name")

    if not roll_col or roll_col not in df.columns:
        return {
            "error": "Mandatory column 'Roll No' not identified in template",
            "inserted_count": 0,
            "updated_count": 0,
            "duplicate_count": 0,
            "failed_count": len(df),
            "failed_records": [{"row": 0, "reason": "Missing Roll No column mapping"}],
        }

    for idx, row in df.iterrows():
        row_num = idx + 2
        raw_roll = clean_val(row.get(roll_col))
        raw_org = clean_val(row.get(org_col)) if org_col else None

        if not raw_roll:
            failed_count += 1
            failed_records.append({"row": row_num, "roll_no": "BLANK", "reason": "Roll No is required"})
            continue
        if not raw_org:
            raw_org = "Independent Internship"

        # Check if student exists in DB or create placeholder
        student = db.query(Student).filter(Student.roll_no == raw_roll).first()
        student_id = student.id if student else None

        # Build parsed dict
        row_data = {"roll_no": raw_roll, "organization_name": raw_org}
        for field, orig_c in field_to_col.items():
            if orig_c in row:
                val = clean_val(row[orig_c])
                if val is not None:
                    if field in ["start_date", "end_date"]:
                        row_data[field] = parse_date(val)
                    elif field == "stipend_amount":
                        try:
                            row_data[field] = float(val)
                        except ValueError:
                            row_data[field] = None
                    elif field == "duration_weeks":
                        try:
                            row_data[field] = int(float(val))
                        except ValueError:
                            row_data[field] = None
                    else:
                        row_data[field] = val

        # Calculate duration if not provided
        s_date = row_data.get("start_date")
        e_date = row_data.get("end_date")
        if not row_data.get("duration_weeks") and s_date and e_date:
            row_data["duration_weeks"] = calculate_duration_weeks(s_date, e_date)

        # Calculate stipend range if not provided
        stipend = row_data.get("stipend_amount")
        if not row_data.get("stipend_range") and stipend is not None:
            if stipend <= 0:
                row_data["stipend_range"] = "Unpaid"
            elif stipend < 10000:
                row_data["stipend_range"] = "< ₹10,000"
            elif stipend <= 25000:
                row_data["stipend_range"] = "₹10,000 - ₹25,000"
            else:
                row_data["stipend_range"] = "> ₹25,000"

        try:
            # Check if internship record already exists for this student and organization
            existing = db.query(Internship).filter(
                Internship.roll_no == raw_roll,
                Internship.name_of_organization == raw_org
            ).first()

            row_data["name_of_organization"] = raw_org
            if "organization_name" in row_data:
                del row_data["organization_name"]

            if existing:
                for k, v in row_data.items():
                    if v is not None and hasattr(existing, k):
                        setattr(existing, k, v)
                if student_id:
                    existing.student_id = student_id
                existing.updated_by_user_id = user_id
                updated_count += 1
                duplicate_count += 1
            else:
                new_internship = Internship(
                    student_id=student_id,
                    created_by_user_id=user_id,
                    **row_data
                )
                db.add(new_internship)
                inserted_count += 1

        except Exception as e:
            failed_count += 1
            failed_records.append({"row": row_num, "roll_no": raw_roll, "reason": str(e)})

    db.commit()

    history = ExcelImportHistory(
        file_name=filename,
        template_type="internship",
        total_rows=len(df),
        inserted_count=inserted_count,
        updated_count=updated_count,
        duplicate_count=duplicate_count,
        failed_count=failed_count,
        failed_records_json=json.dumps(failed_records[:200]),
        status="completed" if failed_count == 0 else ("partial" if inserted_count + updated_count > 0 else "failed"),
        uploaded_by_user_id=user_id,
    )
    db.add(history)
    db.commit()

    return {
        "history_id": history.id,
        "template_type": "internship",
        "total_records": len(df),
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "duplicate_count": duplicate_count,
        "failed_count": failed_count,
        "failed_records": failed_records,
        "message": f"Successfully processed {len(df)} internship records ({inserted_count} new, {updated_count} updated, {failed_count} failed).",
    }

def export_failed_records_excel(failed_records: list[dict]) -> bytes:
    df = pd.DataFrame(failed_records)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Failed Records")
    return output.getvalue()
