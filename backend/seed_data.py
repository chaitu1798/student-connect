import os
import sys
from datetime import date, datetime, timezone
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.organization import College, Branch, Organization
from app.models.student import (
    Student,
    StudentContact,
    StudentAcademic,
    StudentPrivateData,
    StudentAddress,
    StudentConsent,
    StudentPublicationSetting,
)
from app.models.internship import Internship
from app.models.staging import ImportJob, ImportRow, ImportChange
from app.utils.security import hash_password, calculate_duration_weeks

def generate_sample_templates():
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    os.makedirs(template_dir, exist_ok=True)

    # 1. Student Template (All 41 fields including legacy Column1)
    student_headers = [
        "S.No.",
        "Email Address (Recorded)",
        "Roll No.",
        "Full Name (As per SSC)",
        "Column1",
        "Branch",
        "Branch Code",
        "Gender",
        "Contact No.",
        "Parent Contact No.",
        "Corrected Placements Email ID",
        "Alternate Personal Email ID",
        "UG/B.Tech CGPA",
        "UG Year of Pass",
        "No. of Backlogs",
        "First Name",
        "Middle Name",
        "Last Name",
        "Date of Birth",
        "CRT Registered (Y/N)",
        "Xth Grading System",
        "Enter Xth CGPA/Percentage",
        "Grade X Year of Pass",
        "Name of the School",
        "Study after Xth",
        "XIIth/Diploma Grading System",
        "Enter XIIth/Diploma Percentage/CGPA",
        "Grade XIIth/Diploma Year of Pass",
        "XIIth/Diploma College Name",
        "Admission Type",
        "Entrance Exam taken for Admission",
        "EAPCET/E-CET Rank",
        "Father Name",
        "Father Occupation",
        "Languages Known",
        "Caste",
        "Full Residential Address",
        "PAN Card Number",
        "Aadhaar Number",
    ]

    sample_student_rows = [
        {
            "S.No.": "1",
            "Email Address (Recorded)": "rahul.sharma@institution.edu",
            "Roll No.": "21A91A0501",
            "Full Name (As per SSC)": "SHARMA RAHUL KUMAR",
            "Column1": "LEGACY_DATA_REV_01",
            "Branch": "Computer Science & Engineering",
            "Branch Code": "CSE",
            "Gender": "Male",
            "Contact No.": "9876543210",
            "Parent Contact No.": "9876543211",
            "Corrected Placements Email ID": "rahul.placement@institution.edu",
            "Alternate Personal Email ID": "rahul.personal@gmail.com",
            "UG/B.Tech CGPA": 8.75,
            "UG Year of Pass": 2025,
            "No. of Backlogs": 0,
            "First Name": "Rahul",
            "Middle Name": "Kumar",
            "Last Name": "Sharma",
            "Date of Birth": "2003-05-14",
            "CRT Registered (Y/N)": "Y",
            "Xth Grading System": "CGPA",
            "Enter Xth CGPA/Percentage": "9.8",
            "Grade X Year of Pass": 2019,
            "Name of the School": "Delhi Public School",
            "Study after Xth": "Intermediate",
            "XIIth/Diploma Grading System": "Marks/Percentage",
            "Enter XIIth/Diploma Percentage/CGPA": "94.5%",
            "Grade XIIth/Diploma Year of Pass": 2021,
            "XIIth/Diploma College Name": "Sri Chaitanya Junior College",
            "Admission Type": "Convenor",
            "Entrance Exam taken for Admission": "EAPCET",
            "EAPCET/E-CET Rank": "3420",
            "Father Name": "Rajesh Sharma",
            "Father Occupation": "Govt Employee",
            "Languages Known": "English, Hindi, Telugu",
            "Caste": "OC",
            "Full Residential Address": "Flat 302, Green Valley Apartments, Hyderabad",
            "PAN Card Number": "ABCPS1234F",
            "Aadhaar Number": "542389104521",
        },
        {
            "S.No.": "2",
            "Email Address (Recorded)": "priya.verma@institution.edu",
            "Roll No.": "21A91A0502",
            "Full Name (As per SSC)": "VERMA PRIYA ANAND",
            "Column1": "LEGACY_DATA_REV_02",
            "Branch": "Computer Science & Engineering",
            "Branch Code": "CSE",
            "Gender": "Female",
            "Contact No.": "9876543220",
            "Parent Contact No.": "9876543221",
            "Corrected Placements Email ID": "priya.placement@institution.edu",
            "Alternate Personal Email ID": "priya.verma@gmail.com",
            "UG/B.Tech CGPA": 9.12,
            "UG Year of Pass": 2025,
            "No. of Backlogs": 0,
            "First Name": "Priya",
            "Middle Name": "Anand",
            "Last Name": "Verma",
            "Date of Birth": "2003-08-22",
            "CRT Registered (Y/N)": "Y",
            "Xth Grading System": "CGPA",
            "Enter Xth CGPA/Percentage": "10.0",
            "Grade X Year of Pass": 2019,
            "Name of the School": "Kendriya Vidyalaya",
            "Study after Xth": "Intermediate",
            "XIIth/Diploma Grading System": "Percentage",
            "Enter XIIth/Diploma Percentage/CGPA": "96.2%",
            "Grade XIIth/Diploma Year of Pass": 2021,
            "XIIth/Diploma College Name": "Narayana Junior College",
            "Admission Type": "Convenor",
            "Entrance Exam taken for Admission": "EAPCET",
            "EAPCET/E-CET Rank": "1840",
            "Father Name": "Anand Verma",
            "Father Occupation": "Engineer",
            "Languages Known": "English, Hindi",
            "Caste": "BC-B",
            "Full Residential Address": "Plot 45, Jubilee Enclave, Hyderabad",
            "PAN Card Number": "BKIPV4321A",
            "Aadhaar Number": "764289012345",
        }
    ]

    df_student = pd.DataFrame(sample_student_rows, columns=student_headers)
    student_template_path = os.path.join(template_dir, "student_template.xlsx")
    with pd.ExcelWriter(student_template_path, engine="openpyxl") as writer:
        df_student.to_excel(writer, index=False, sheet_name="Student_Template")

    # 2. Internship Template (All 22 fields)
    internship_headers = [
        "S.No.",
        "Roll No.",
        "Full Name (As per SSC)",
        "Branch",
        "Name of College",
        "Name of Organization (Internship)",
        "Organization District",
        "Category",
        "Role",
        "Mode of Internship",
        "Internship Type",
        "Stipend (₹/Month)",
        "Start Date",
        "End Date",
        "Certificate Received",
        "Duration in Weeks (Auto)",
        "Address of Organization",
        "Stipend Range",
        "Internship Offered By",
        "Regular Internship (AEP / IDEA LAB)",
        "Gender",
        "Contact No.",
    ]

    sample_internship_rows = [
        {
            "S.No.": "1",
            "Roll No.": "21A91A0501",
            "Full Name (As per SSC)": "SHARMA RAHUL KUMAR",
            "Branch": "Computer Science & Engineering",
            "Name of College": "Vignan's Institute Of Information Technology",
            "Name of Organization (Internship)": "Microsoft India R&D",
            "Organization District": "Hyderabad",
            "Category": "Technical",
            "Role": "Software Engineer Intern",
            "Mode of Internship": "Hybrid",
            "Internship Type": "Paid",
            "Stipend (₹/Month)": 50000,
            "Start Date": "2024-05-01",
            "End Date": "2024-07-31",
            "Certificate Received": "Yes",
            "Duration in Weeks (Auto)": 13,
            "Address of Organization": "Gachibowli, Hyderabad, Telangana",
            "Stipend Range": "> ₹25,000",
            "Internship Offered By": "On-Campus Drive",
            "Regular Internship (AEP / IDEA LAB)": "Regular",
            "Gender": "Male",
            "Contact No.": "9876543210",
        }
    ]

    df_internship = pd.DataFrame(sample_internship_rows, columns=internship_headers)
    internship_template_path = os.path.join(template_dir, "internship_template.xlsx")
    with pd.ExcelWriter(internship_template_path, engine="openpyxl") as writer:
        df_internship.to_excel(writer, index=False, sheet_name="Internship_Template")

    print(f"Generated sample templates in {template_dir}")

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Roles & Users
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@institution.edu",
                full_name="Super Administrator",
                role="SUPER_ADMIN",
                hashed_password=hash_password("ChangeMe123!"),
                must_change_password=True,
                mfa_enabled=False,
            )
            db.add(admin)

        client = db.query(User).filter(User.username == "client").first()
        if not client:
            client = User(
                username="client",
                email="client@institution.edu",
                full_name="Placement & Records Officer",
                role="CLIENT",
                hashed_password=hash_password("Client123!"),
                must_change_password=False,
                mfa_enabled=False,
            )
            db.add(client)

        reviewer = db.query(User).filter(User.username == "reviewer").first()
        if not reviewer:
            reviewer = User(
                username="reviewer",
                email="reviewer@institution.edu",
                full_name="Academic Verification Officer",
                role="REVIEWER",
                hashed_password=hash_password("Reviewer123!"),
                must_change_password=False,
                mfa_enabled=False,
            )
            db.add(reviewer)

        # 2. Colleges & Branches
        college = db.query(College).filter(College.code == "UCE").first()
        if not college:
            college = College(code="UCE", name="Vignan's Institute Of Information Technology")
            db.add(college)
            db.flush()

        branches_list = [
            ("CSE", "Computer Science & Engineering"),
            ("ECE", "Electronics & Communication Engineering"),
            ("IT", "Information Technology"),
            ("EEE", "Electrical & Electronics Engineering"),
            ("MECH", "Mechanical Engineering"),
            ("CIVIL", "Civil Engineering"),
            ("AI_DS", "Artificial Intelligence & Data Science"),
        ]
        branch_objs = {}
        for code, bname in branches_list:
            b = db.query(Branch).filter(Branch.code == code).first()
            if not b:
                b = Branch(code=code, name=bname)
                db.add(b)
                db.flush()
            branch_objs[code] = b

        # 3. Organizations
        org_list = [
            ("Microsoft India R&D", "Hyderabad", "Technical"),
            ("Amazon Development Centre", "Hyderabad", "Technical"),
            ("Qualcomm India", "Hyderabad", "Technical"),
            ("TCS Research & Innovation", "Hyderabad", "Research"),
            ("AICTE Virtual Internships", "Online", "Research"),
        ]
        org_objs = {}
        for oname, odist, ocat in org_list:
            org = db.query(Organization).filter(Organization.name == oname).first()
            if not org:
                org = Organization(name=oname, district=odist, category=ocat)
                db.add(org)
                db.flush()
            org_objs[oname] = org

        db.commit()

        # 4. Realistic Students Data
        students_info = [
            {
                "roll_no": "21A91A0501",
                "full_name": "SHARMA RAHUL KUMAR",
                "first_name": "Rahul",
                "last_name": "Sharma",
                "branch_code": "CSE",
                "branch": "Computer Science & Engineering",
                "column1": "LEGACY_DATA_REV_01",
                "gender": "Male",
                "dob": "2003-05-14",
                "phone": "9876543210",
                "parent_phone": "9876543211",
                "email": "rahul.sharma@institution.edu",
                "placement_email": "rahul.placement@institution.edu",
                "cgpa": 8.75,
                "yop": 2025,
                "backlogs": 0,
                "crt": "Y",
                "pan": "ABCPS1234F",
                "aadhaar": "542389104521",
                "address": "Flat 302, Green Valley Apartments, Hyderabad",
                "is_public": True,
            },
            {
                "roll_no": "21A91A0502",
                "full_name": "VERMA PRIYA ANAND",
                "first_name": "Priya",
                "last_name": "Verma",
                "branch_code": "CSE",
                "branch": "Computer Science & Engineering",
                "column1": "LEGACY_DATA_REV_02",
                "gender": "Female",
                "dob": "2003-08-22",
                "phone": "9876543220",
                "parent_phone": "9876543221",
                "email": "priya.verma@institution.edu",
                "placement_email": "priya.placement@institution.edu",
                "cgpa": 9.12,
                "yop": 2025,
                "backlogs": 0,
                "crt": "Y",
                "pan": "BKIPV4321A",
                "aadhaar": "764289012345",
                "address": "Plot 45, Jubilee Enclave, Hyderabad",
                "is_public": True,
            },
            {
                "roll_no": "21A91A0415",
                "full_name": "K REDDY VENKATA SAI",
                "first_name": "Venkata",
                "last_name": "Sai Reddy",
                "branch_code": "ECE",
                "branch": "Electronics & Communication Engineering",
                "gender": "Male",
                "dob": "2003-11-05",
                "phone": "9876543230",
                "parent_phone": "9876543231",
                "email": "sai.reddy@institution.edu",
                "cgpa": 7.95,
                "yop": 2025,
                "backlogs": 1,
                "crt": "N",
                "is_public": True,
            },
            {
                "roll_no": "21A91A1208",
                "full_name": "ANANYA MUKHERJEE",
                "first_name": "Ananya",
                "last_name": "Mukherjee",
                "branch_code": "IT",
                "branch": "Information Technology",
                "gender": "Female",
                "dob": "2003-03-19",
                "phone": "9876543240",
                "parent_phone": "9876543241",
                "email": "ananya.m@institution.edu",
                "cgpa": 8.45,
                "yop": 2025,
                "backlogs": 0,
                "crt": "Y",
                "is_public": True,
            },
            {
                "roll_no": "20A91A0322",
                "full_name": "MOHAMMED AFZAL",
                "first_name": "Mohammed",
                "last_name": "Afzal",
                "branch_code": "MECH",
                "branch": "Mechanical Engineering",
                "gender": "Male",
                "dob": "2002-09-12",
                "phone": "9876543250",
                "email": "afzal.m@institution.edu",
                "cgpa": 7.30,
                "yop": 2024,
                "backlogs": 0,
                "crt": "Y",
                "is_public": False,
            }
        ]

        for s in students_info:
            existing = db.query(Student).filter(Student.roll_no == s["roll_no"]).first()
            if not existing:
                student = Student(
                    roll_no=s["roll_no"],
                    full_name=s["full_name"],
                    first_name=s["first_name"],
                    last_name=s["last_name"],
                    branch=s["branch"],
                    branch_code=s["branch_code"],
                    name_of_college="Vignan's Institute Of Information Technology",
                    college_id=college.id,
                    branch_id=branch_objs.get(s["branch_code"], branch_objs["CSE"]).id,
                    column1=s.get("column1", "LEGACY_DATA_REV_00"),
                )
                db.add(student)
                db.flush()

                contacts = StudentContact(
                    student_id=student.id,
                    recorded_email=s.get("email"),
                    corrected_placement_email=s.get("placement_email"),
                    contact_number=s.get("phone"),
                    parent_contact_number=s.get("parent_phone"),
                )
                db.add(contacts)

                academics = StudentAcademic(
                    student_id=student.id,
                    ug_cgpa=s.get("cgpa"),
                    ug_year_of_passing=s.get("yop"),
                    number_of_backlogs=s.get("backlogs", 0),
                    crt_registered=s.get("crt", "N"),
                    admission_type="Convenor",
                    study_after_x="Intermediate",
                )
                db.add(academics)

                priv = StudentPrivateData(
                    student_id=student.id,
                    gender=s.get("gender"),
                    date_of_birth=s.get("dob"),
                    pan_number=s.get("pan"),
                    aadhaar_number=s.get("aadhaar"),
                    languages_known="English, Telugu, Hindi",
                )
                db.add(priv)

                addr = StudentAddress(
                    student_id=student.id,
                    full_residential_address=s.get("address", "Hyderabad"),
                )
                db.add(addr)

                pub = StudentPublicationSetting(
                    student_id=student.id,
                    is_public_approved=s.get("is_public", False),
                    publish_gender=True,
                    publish_cgpa=True,
                    publish_internships=True,
                    approved_at=datetime.now(timezone.utc) if s.get("is_public") else None,
                )
                db.add(pub)

                consent = StudentConsent(student_id=student.id, consent_given=True)
                db.add(consent)

        db.commit()

        # 5. Internships
        internships_info = [
            {
                "roll_no": "21A91A0501",
                "org_name": "Microsoft India R&D",
                "role": "Software Engineer Intern",
                "mode": "Hybrid",
                "type": "Paid",
                "stipend": 50000,
                "start": date(2024, 5, 1),
                "end": date(2024, 7, 31),
                "cert": "Yes",
            },
            {
                "roll_no": "21A91A0501",
                "org_name": "AICTE Virtual Internships",
                "role": "Cybersecurity Intern",
                "mode": "Online",
                "type": "Unpaid",
                "stipend": 0,
                "start": date(2023, 8, 1),
                "end": date(2023, 10, 1),
                "cert": "Yes",
            },
            {
                "roll_no": "21A91A0502",
                "org_name": "Amazon Development Centre",
                "role": "Cloud Solutions Intern",
                "mode": "Offline",
                "type": "Paid",
                "stipend": 60000,
                "start": date(2024, 6, 1),
                "end": date(2024, 8, 31),
                "cert": "Yes",
            },
            {
                "roll_no": "21A91A0415",
                "org_name": "Qualcomm India",
                "role": "Hardware Verification Intern",
                "mode": "Offline",
                "type": "Paid",
                "stipend": 45000,
                "start": date(2024, 5, 15),
                "end": date(2024, 7, 15),
                "cert": "No",
            },
            {
                "roll_no": "21A91A1208",
                "org_name": "TCS Research & Innovation",
                "role": "Data Science Research Intern",
                "mode": "Hybrid",
                "type": "Paid",
                "stipend": 25000,
                "start": date(2024, 4, 1),
                "end": date(2024, 6, 30),
                "cert": "Yes",
            }
        ]

        for i in internships_info:
            existing = db.query(Internship).filter(
                Internship.roll_no == i["roll_no"],
                Internship.name_of_organization == i["org_name"]
            ).first()
            if not existing:
                student = db.query(Student).filter(Student.roll_no == i["roll_no"]).first()
                org = org_objs.get(i["org_name"])
                duration = calculate_duration_weeks(i["start"], i["end"])
                intern = Internship(
                    student_id=student.id if student else None,
                    organization_id=org.id if org else None,
                    roll_no=i["roll_no"],
                    full_name=student.full_name if student else None,
                    branch=student.branch if student else None,
                    name_of_organization=i["org_name"],
                    organization_district=org.district if org else "Hyderabad",
                    category=org.category if org else "Technical",
                    role=i["role"],
                    mode_of_internship=i["mode"],
                    internship_type=i["type"],
                    stipend_amount=i["stipend"],
                    start_date=i["start"],
                    end_date=i["end"],
                    duration_weeks=duration,
                    certificate_received=i["cert"],
                )
                db.add(intern)

        # 6. Seed a sample Staged Import Job in 'SUBMITTED' state for demonstration
        sample_job = db.query(ImportJob).filter(ImportJob.file_name == "Spring_2026_Batch_Updates.xlsx").first()
        if not sample_job:
            sample_job = ImportJob(
                client_user_id=client.id,
                file_name="Spring_2026_Batch_Updates.xlsx",
                template_type="student",
                status="SUBMITTED",
                total_rows=2,
                valid_rows=0,
                diff_rows=2,
                error_rows=0,
                submitted_at=datetime.now(timezone.utc),
                remarks="Updated CGPAs after 7th semester results announcement",
            )
            db.add(sample_job)
            db.flush()

            # Row 1 with CGPA diff
            r1 = ImportRow(
                import_job_id=sample_job.id,
                row_index=2,
                roll_number="21A91A0501",
                status="DIFF_DETECTED",
                raw_data_json='{"Roll No.": "21A91A0501", "Full Name": "SHARMA RAHUL KUMAR", "CGPA": 8.95}',
                normalized_data_json='{"roll_no": "21A91A0501", "full_name": "SHARMA RAHUL KUMAR", "ug_cgpa": 8.95}',
            )
            db.add(r1)
            db.flush()

            c1 = ImportChange(
                import_row_id=r1.id,
                entity_type="academic",
                entity_id="21A91A0501",
                field_name="ug_cgpa",
                old_value="8.75",
                new_value="8.95",
                is_selected=True,
            )
            db.add(c1)

            # Row 2 with Backlog diff
            r2 = ImportRow(
                import_job_id=sample_job.id,
                row_index=3,
                roll_number="21A91A0415",
                status="DIFF_DETECTED",
                raw_data_json='{"Roll No.": "21A91A0415", "Full Name": "K REDDY VENKATA SAI", "Backlogs": 0}',
                normalized_data_json='{"roll_no": "21A91A0415", "full_name": "K REDDY VENKATA SAI", "number_of_backlogs": 0}',
            )
            db.add(r2)
            db.flush()

            c2 = ImportChange(
                import_row_id=r2.id,
                entity_type="academic",
                entity_id="21A91A0415",
                field_name="number_of_backlogs",
                old_value="1",
                new_value="0",
                is_selected=True,
            )
            db.add(c2)

        db.commit()
        print("Database seeded successfully with enterprise normalized tables, roles, and submitted approval jobs!")
    finally:
        db.close()

if __name__ == "__main__":
    generate_sample_templates()
    seed_database()
