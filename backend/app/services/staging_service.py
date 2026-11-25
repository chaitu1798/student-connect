import io
import json
import math
from datetime import datetime, timezone, date
import pandas as pd
from sqlalchemy.orm import Session
from app.models.student import (
    Student,
    StudentContact,
    StudentAcademic,
    StudentPrivateData,
    StudentAddress,
    StudentConsent,
    StudentPublicationSetting,
)
from app.models.organization import Organization, Branch, College
from app.models.internship import Internship
from app.models.staging import (
    ImportJob,
    ImportRow,
    ImportChange,
    ApprovalAction,
)
from app.utils.security import verify_file_signature, calculate_duration_weeks
from app.services.audit_service import log_audit

STUDENT_FIELD_SYNONYMS = {
    "s_no": ["s.no", "s.no.", "sno", "serial no", "serial number", "sl no"],
    "recorded_email": ["email address (recorded)", "recorded email", "email address", "email", "recorded email id"],
    "roll_no": ["roll no", "roll no.", "roll number", "rollno", "ht no", "hall ticket no", "registration no"],
    "full_name": ["full name (as per ssc)", "full name", "student name", "name as per ssc", "name"],
    "first_name": ["first name", "firstname"],
    "middle_name": ["middle name", "middlename"],
    "last_name": ["last name", "lastname", "surname"],
    "column1": ["column1", "column 1", "remarks", "notes"],
    "branch": ["branch", "department", "stream", "course"],
    "branch_code": ["branch code", "dept code", "branch_code"],
    "name_of_college": ["name of college", "college name", "college"],
    "gender": ["gender", "sex"],
    "contact_number": ["contact no", "contact no.", "contact number", "phone", "student mobile", "mobile no", "mobile"],
    "parent_contact_number": ["parent contact no", "parent contact no.", "parent contact number", "parent mobile", "father mobile"],
    "corrected_placement_email": ["corrected placements email id", "corrected placement email", "placements email", "placement email"],
    "alternate_personal_email": ["alternate personal email id", "alternate email", "personal email", "personal email id"],
    "ug_cgpa": ["ug/b.tech cgpa", "ug cgpa", "b.tech cgpa", "cgpa", "btech cgpa"],
    "ug_year_of_passing": ["ug year of pass", "year of pass", "passing year", "ug passing year", "ug year of passing", "yop"],
    "number_of_backlogs": ["no. of backlogs", "backlogs", "no of backlogs", "standing backlogs", "number of backlogs"],
    "date_of_birth": ["date of birth", "dob", "birth date"],
    "crt_registered": ["crt registered (y/n)", "crt registered", "crt", "crt registration"],
    "x_grading_system": ["xth grading system", "10th grading system", "ssc grading system"],
    "x_cgpa_percentage": ["enter xth cgpa/percentage", "xth cgpa", "xth percentage", "10th cgpa", "10th percentage", "ssc marks"],
    "x_year_of_passing": ["grade x year of pass", "10th year of pass", "ssc year of pass", "xth year of passing"],
    "x_school_name": ["name of the school", "school name", "10th school name", "ssc school"],
    "study_after_x": ["study after xth", "study after 10th", "intermediate or diploma"],
    "xii_grading_system": ["xiith/diploma grading system", "12th grading system", "diploma grading system", "inter grading system"],
    "xii_cgpa_percentage": ["enter xiith/diploma percentage/cgpa", "12th percentage", "inter percentage", "diploma percentage", "xiith cgpa", "xii cgpa/percentage"],
    "xii_year_of_passing": ["grade xiith/diploma year of pass", "12th year of pass", "inter year of pass", "diploma year of pass", "year of passing"],
    "xii_college_name": ["xiith/diploma college name", "junior college name", "diploma college name", "12th college name"],
    "admission_type": ["admission type", "type of admission", "quota"],
    "entrance_exam": ["entrance exam taken for admission", "entrance exam", "exam taken"],
    "entrance_rank": ["eapcet/e-cet rank", "eapcet rank", "ecet rank", "entrance rank", "rank"],
    "father_name": ["father name", "father's name", "parent name"],
    "father_occupation": ["father occupation", "father's occupation", "parent occupation"],
    "languages_known": ["languages known", "languages"],
    "caste": ["caste", "category/caste", "social category"],
    "full_residential_address": ["full residential address", "residential address", "address", "permanent address"],
    "pan_number": ["pan card number", "pan number", "pan", "pan no"],
    "aadhaar_number": ["aadhaar number", "aadhaar card number", "aadhaar", "aadhaar no", "aadhar number", "aadhar"],
}

INTERNSHIP_FIELD_SYNONYMS = {
    "s_no": ["s.no", "s.no.", "sno", "sl no"],
    "roll_no": ["roll no", "roll no.", "roll number", "rollno", "ht no", "hall ticket no"],
    "full_name": ["full name (as per ssc)", "full name", "student name", "name as per ssc"],
    "branch": ["branch", "department", "stream"],
    "name_of_college": ["name of college", "college name", "college"],
    "name_of_organization": ["name of organization (internship)", "name of organization", "organization name", "company name", "organization", "company"],
    "organization_district": ["organization district", "district", "company location district"],
    "category": ["category", "internship domain", "domain"],
    "role": ["role", "designation", "job role", "internship role"],
    "mode_of_internship": ["mode of internship", "mode", "internship mode", "work mode"],
    "internship_type": ["internship type", "type", "paid/unpaid"],
    "stipend_amount": ["stipend (₹/month)", "stipend amount", "stipend", "stipend per month", "monthly stipend"],
    "start_date": ["start date", "from date", "commencement date", "joining date"],
    "end_date": ["end date", "to date", "completion date"],
    "certificate_received": ["certificate received", "certificate status", "certificate submitted"],
    "duration_weeks": ["duration (weeks)", "duration in weeks", "duration", "duration in weeks (auto)"],
    "organization_address": ["address of organization", "organization address", "company address"],
    "stipend_range": ["stipend range", "salary range"],
    "internship_offered_by": ["internship offered by", "offered by", "platform/offered by"],
    "regular_internship": ["regular internship (aep / idea lab)", "regular internship", "internship category type"],
    "gender": ["gender", "sex"],
    "contact_number": ["contact no", "contact no.", "contact number", "student contact", "phone"],
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
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            pass
    return None

def map_headers(columns: list[str], template_type: str) -> dict[str, str]:
    synonyms = STUDENT_FIELD_SYNONYMS if template_type == "student" else INTERNSHIP_FIELD_SYNONYMS
    mapping = {}
    for col in columns:
        col_clean = str(col).strip().lower()
        matched = None
        for field, alt_names in synonyms.items():
            if col_clean == field or col_clean in alt_names:
                matched = field
                break
        if matched:
            mapping[col] = matched
    return mapping

def read_dataframe(file_bytes: bytes, filename: str) -> pd.DataFrame:
    fn = filename.lower()
    if fn.endswith('.csv'):
        return pd.read_csv(io.BytesIO(file_bytes))
    elif fn.endswith('.xls'):
        return pd.read_excel(io.BytesIO(file_bytes), engine="xlrd")
    else:
        return pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")

def create_staged_import(
    db: Session,
    client_user_id: str | None,
    file_bytes: bytes,
    filename: str,
    template_type: str
) -> ImportJob:
    """
    Parses file into staging tables (ImportJob, ImportRow, ImportChange)
    Compares incoming values against master records to produce a Diff view.
    Does NOT overwrite master database!
    """
    if not verify_file_signature(file_bytes, filename):
        raise ValueError("Invalid file format or malicious file signature detected")

    df = read_dataframe(file_bytes, filename)
    cols = [str(c) for c in df.columns]
    mapping = map_headers(cols, template_type)
    field_to_col = {v: k for k, v in mapping.items()}

    roll_col = field_to_col.get("roll_no")
    if not roll_col or roll_col not in df.columns:
        raise ValueError("Mandatory column 'Roll No' not detected in spreadsheet headers")

    job = ImportJob(
        client_user_id=client_user_id,
        file_name=filename,
        template_type=template_type,
        status="DRAFT",
        total_rows=len(df),
    )
    db.add(job)
    db.flush()

    valid_count = 0
    diff_count = 0
    error_count = 0

    seen_rolls = set()

    for idx, raw_row in df.iterrows():
        row_num = idx + 2
        raw_roll = clean_val(raw_row.get(roll_col))

        if not raw_roll:
            error_count += 1
            i_row = ImportRow(
                import_job_id=job.id,
                row_index=row_num,
                roll_number="MISSING",
                status="ERROR",
                raw_data_json=json.dumps({str(k): clean_val(v) for k, v in raw_row.items()}),
                error_message="Roll Number is required",
            )
            db.add(i_row)
            continue

        raw_roll = raw_roll.upper()
        row_dict = {}
        for f_name, orig_c in field_to_col.items():
            if orig_c in raw_row:
                row_dict[f_name] = clean_val(raw_row[orig_c])

        # Check existing student in master DB
        existing_student = db.query(Student).filter(Student.roll_no == raw_roll).first()
        is_duplicate = raw_roll in seen_rolls
        seen_rolls.add(raw_roll)

        row_status = "VALID"
        changes_to_record = []

        if template_type == "student":
            if existing_student:
                # Compare fields for diff
                # 1. Student main fields
                main_fields = ["full_name", "first_name", "last_name", "branch", "branch_code", "name_of_college", "column1"]
                for mf in main_fields:
                    new_v = row_dict.get(mf)
                    old_v = getattr(existing_student, mf, None)
                    if new_v is not None and str(new_v).strip() != str(old_v or "").strip():
                        changes_to_record.append(("student", existing_student.id, mf, str(old_v or ""), str(new_v)))

                # 2. Academics
                ac = existing_student.academics
                if ac:
                    for af in ["ug_cgpa", "ug_year_of_passing", "number_of_backlogs", "crt_registered"]:
                        new_v = row_dict.get(af)
                        old_v = getattr(ac, af, None)
                        if new_v is not None and str(new_v).strip() != str(old_v or "").strip():
                            changes_to_record.append(("academic", ac.id, af, str(old_v or ""), str(new_v)))

                # 3. Contacts
                ct = existing_student.contacts
                if ct:
                    for cf in ["contact_number", "recorded_email", "corrected_placement_email", "alternate_personal_email", "parent_contact_number"]:
                        new_v = row_dict.get(cf)
                        old_v = getattr(ct, cf, None)
                        if new_v is not None and str(new_v).strip() != str(old_v or "").strip():
                            changes_to_record.append(("contact", ct.id, cf, str(old_v or ""), str(new_v)))

                if changes_to_record:
                    row_status = "DIFF_DETECTED"
                    diff_count += 1
                else:
                    valid_count += 1
            else:
                valid_count += 1

        elif template_type == "internship":
            org_name = row_dict.get("name_of_organization") or "Corporate Organization"
            existing_internship = db.query(Internship).filter(
                Internship.roll_no == raw_roll,
                Internship.name_of_organization == org_name
            ).first()

            if existing_internship:
                for inf in ["role", "category", "mode_of_internship", "internship_type", "stipend_amount", "certificate_received"]:
                    new_v = row_dict.get(inf)
                    old_v = getattr(existing_internship, inf, None)
                    if new_v is not None and str(new_v).strip() != str(old_v or "").strip():
                        changes_to_record.append(("internship", existing_internship.id, inf, str(old_v or ""), str(new_v)))

                if changes_to_record:
                    row_status = "DIFF_DETECTED"
                    diff_count += 1
                else:
                    valid_count += 1
            else:
                valid_count += 1

        # Create staged row
        i_row = ImportRow(
            import_job_id=job.id,
            row_index=row_num,
            roll_number=raw_roll,
            status=row_status,
            raw_data_json=json.dumps({str(k): clean_val(v) for k, v in raw_row.items()}),
            normalized_data_json=json.dumps(row_dict),
            error_message="Duplicate row in spreadsheet" if is_duplicate else None,
        )
        db.add(i_row)
        db.flush()

        # Add diff changes
        for entity_type, entity_id, field_name, old_v, new_v in changes_to_record:
            chg = ImportChange(
                import_row_id=i_row.id,
                entity_type=entity_type,
                entity_id=str(entity_id),
                field_name=field_name,
                old_value=old_v,
                new_value=new_v,
                is_selected=True,
            )
            db.add(chg)

    job.valid_rows = valid_count
    job.diff_rows = diff_count
    job.error_rows = error_count
    db.commit()

    log_audit(db, client_user_id, "client", "IMPORT_STAGE", "import_job", job.id, f"Uploaded {filename}: {len(df)} rows parsed into staging")
    return job

def apply_approved_job(db: Session, job: ImportJob, reviewer_id: str, remarks: str | None = None):
    """
    Transactionally applies approved changes from staging to normalized master tables.
    """
    for row in job.rows:
        if row.status == "ERROR" or not row.normalized_data_json:
            continue

        data = json.loads(row.normalized_data_json)
        roll_no = row.roll_number

        if job.template_type == "student":
            student = db.query(Student).filter(Student.roll_no == roll_no).first()
            if not student:
                # Insert master student
                student = Student(
                    roll_no=roll_no,
                    full_name=data.get("full_name") or roll_no,
                    first_name=data.get("first_name"),
                    middle_name=data.get("middle_name"),
                    last_name=data.get("last_name"),
                    branch=data.get("branch"),
                    branch_code=data.get("branch_code"),
                    name_of_college=data.get("name_of_college"),
                    column1=data.get("column1"),
                    created_by_user_id=reviewer_id,
                )
                db.add(student)
                db.flush()

                # Add normalized child records
                contacts = StudentContact(
                    student_id=student.id,
                    recorded_email=data.get("recorded_email"),
                    corrected_placement_email=data.get("corrected_placement_email"),
                    alternate_personal_email=data.get("alternate_personal_email"),
                    contact_number=data.get("contact_number"),
                    parent_contact_number=data.get("parent_contact_number"),
                )
                db.add(contacts)

                cgpa = float(data["ug_cgpa"]) if data.get("ug_cgpa") else None
                yop = int(float(data["ug_year_of_passing"])) if data.get("ug_year_of_passing") else None
                backlogs = int(float(data["number_of_backlogs"])) if data.get("number_of_backlogs") else 0
                academics = StudentAcademic(
                    student_id=student.id,
                    ug_cgpa=cgpa,
                    ug_year_of_passing=yop,
                    number_of_backlogs=backlogs,
                    crt_registered=data.get("crt_registered") or "N",
                    x_grading_system=data.get("x_grading_system"),
                    x_cgpa_percentage=data.get("x_cgpa_percentage"),
                    study_after_x=data.get("study_after_x"),
                    xii_grading_system=data.get("xii_grading_system"),
                    xii_cgpa_percentage=data.get("xii_cgpa_percentage"),
                    admission_type=data.get("admission_type"),
                    entrance_exam=data.get("entrance_exam"),
                    entrance_rank=data.get("entrance_rank"),
                )
                db.add(academics)

                priv = StudentPrivateData(
                    student_id=student.id,
                    gender=data.get("gender"),
                    date_of_birth=data.get("date_of_birth"),
                    languages_known=data.get("languages_known"),
                    father_name=data.get("father_name"),
                    father_occupation=data.get("father_occupation"),
                    caste=data.get("caste"),
                    pan_number=data.get("pan_number"),
                    aadhaar_number=data.get("aadhaar_number"),
                )
                db.add(priv)

                addr = StudentAddress(
                    student_id=student.id,
                    full_residential_address=data.get("full_residential_address"),
                )
                db.add(addr)

                pub = StudentPublicationSetting(
                    student_id=student.id,
                    is_public_approved=False,
                    publish_gender=False,
                    publish_cgpa=False,
                    publish_internships=True,
                )
                db.add(pub)

                consent = StudentConsent(student_id=student.id, consent_given=True)
                db.add(consent)

            else:
                # Update existing student according to selected changes
                for chg in row.changes:
                    if not chg.is_selected:
                        continue
                    if chg.entity_type == "student" and hasattr(student, chg.field_name):
                        setattr(student, chg.field_name, chg.new_value)
                    elif chg.entity_type == "academic" and student.academics:
                        val = chg.new_value
                        if chg.field_name in ["ug_cgpa"]:
                            val = float(val) if val else None
                        elif chg.field_name in ["ug_year_of_passing", "number_of_backlogs"]:
                            val = int(float(val)) if val else 0
                        setattr(student.academics, chg.field_name, val)
                    elif chg.entity_type == "contact" and student.contacts:
                        setattr(student.contacts, chg.field_name, chg.new_value)
                student.updated_by_user_id = reviewer_id

        elif job.template_type == "internship":
            student = db.query(Student).filter(Student.roll_no == roll_no).first()
            org_name = data.get("name_of_organization") or "Corporate Organization"
            
            # Find or create organization
            org = db.query(Organization).filter(Organization.name == org_name).first()
            if not org:
                org = Organization(
                    name=org_name,
                    district=data.get("organization_district"),
                    address=data.get("organization_address"),
                    category=data.get("category"),
                )
                db.add(org)
                db.flush()

            existing = db.query(Internship).filter(
                Internship.roll_no == roll_no,
                Internship.name_of_organization == org_name
            ).first()

            s_date = parse_date(data.get("start_date"))
            e_date = parse_date(data.get("end_date"))
            duration = calculate_duration_weeks(s_date, e_date)
            stipend = float(data["stipend_amount"]) if data.get("stipend_amount") else None

            if existing:
                for chg in row.changes:
                    if chg.is_selected and hasattr(existing, chg.field_name):
                        val = chg.new_value
                        if chg.field_name in ["start_date", "end_date"] and val:
                            val = parse_date(val)
                        elif chg.field_name == "stipend_amount" and val:
                            try:
                                val = float(val)
                            except ValueError:
                                val = None
                        elif chg.field_name == "duration_weeks" and val:
                            try:
                                val = int(float(val))
                            except ValueError:
                                val = None
                        setattr(existing, chg.field_name, val)
                if existing.start_date and existing.end_date:
                    existing.duration_weeks = calculate_duration_weeks(existing.start_date, existing.end_date)
                existing.updated_by_user_id = reviewer_id
            else:
                student_gender = None
                if student and hasattr(student, 'private_data') and student.private_data:
                    student_gender = student.private_data.gender

                new_intern = Internship(
                    s_no=data.get("s_no"),
                    student_id=student.id if student else None,
                    roll_no=roll_no,
                    full_name=data.get("full_name") or (student.full_name if student else None),
                    branch=data.get("branch") or (student.branch if student else None),
                    name_of_college=data.get("name_of_college") or (student.name_of_college if student else None),
                    organization_id=org.id,
                    name_of_organization=org_name,
                    organization_district=data.get("organization_district"),
                    organization_address=data.get("organization_address"),
                    category=data.get("category"),
                    role=data.get("role"),
                    mode_of_internship=data.get("mode_of_internship") or "Offline",
                    internship_type=data.get("internship_type") or "Paid",
                    stipend_amount=stipend,
                    stipend_range=data.get("stipend_range"),
                    start_date=s_date,
                    end_date=e_date,
                    duration_weeks=duration,
                    certificate_received=data.get("certificate_received") or "No",
                    internship_offered_by=data.get("internship_offered_by"),
                    regular_internship=data.get("regular_internship"),
                    gender=data.get("gender") or student_gender,
                    contact_number=data.get("contact_number"),
                    created_by_user_id=reviewer_id,
                )
                db.add(new_intern)

    job.status = "APPROVED"
    job.reviewed_at = datetime.now(timezone.utc)
    job.reviewed_by_user_id = reviewer_id
    job.remarks = remarks

    action = ApprovalAction(
        import_job_id=job.id,
        reviewer_id=reviewer_id,
        action="APPROVE",
        remarks=remarks,
    )
    db.add(action)
    db.commit()

    log_audit(db, reviewer_id, "admin", "APPROVE", "import_job", job.id, f"Approved and committed import job {job.file_name} transactionally to master tables")
