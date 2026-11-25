import io
import html
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from app.models.student import Student, StudentAcademic, StudentContact, StudentPrivateData, StudentAddress
from app.models.internship import Internship
from app.models.organization import Organization, Branch

REPORT_COLUMNS = {
    "complete_student": ["Roll No", "Full Name", "Branch", "Branch Code", "CGPA", "Passing Year", "Backlogs", "CRT Registered", "Contact", "Email", "Date of Birth", "Father Name", "Admission Type"],
    "academic": ["Roll No", "Full Name", "Branch", "UG CGPA", "Backlogs", "10th Board", "10th Marks/CGPA", "10th School", "12th/Diploma", "12th Marks/CGPA", "12th College"],
    "internship": ["Roll No", "Student Name", "Branch", "Organization", "District", "Category", "Role", "Mode", "Type", "Stipend (₹/mo)", "Duration (Weeks)", "Start Date", "End Date", "Certificate Received"],
    "organization_wise": ["Roll No", "Student Name", "Branch", "Organization", "District", "Category", "Role", "Mode", "Type", "Stipend (₹/mo)", "Duration (Weeks)", "Start Date", "End Date", "Certificate Received"],
    "backlog": ["Roll No", "Full Name", "Branch", "Backlogs Count", "CGPA", "Passing Year", "Contact"],
    "crt_registered": ["Roll No", "Full Name", "Branch", "CGPA", "Contact", "Placements Email"],
    "without_internships": ["Roll No", "Full Name", "Branch", "CGPA", "Passing Year", "Contact"],
    "certificate_pending": ["Roll No", "Student Name", "Branch", "Organization", "Role", "End Date", "Certificate Received"],
}

def mask_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    clean = str(phone).strip()
    if len(clean) >= 4:
        return "XXXXXX" + clean[-4:]
    return "XXXXXX"

def generate_report_dataframe(db: Session, report_type: str, filters: dict | None = None, mask_sensitive: bool = False) -> pd.DataFrame:
    filters = filters or {}
    default_cols = REPORT_COLUMNS.get(report_type, ["Roll No", "Name", "Branch"])

    if report_type == "complete_student":
        students = db.query(Student).filter(Student.is_archived == False).all()
        data = []
        for s in students:
            ac = s.academics
            ct = s.contacts
            priv = s.private_data
            phone_val = mask_phone(ct.contact_number) if mask_sensitive and ct else (ct.contact_number if ct else None)
            dob_val = "XXXX-XX-XX" if mask_sensitive else (priv.date_of_birth if priv else None)
            father_val = "Confidential" if mask_sensitive else (priv.father_name if priv else None)
            data.append({
                "Roll No": s.roll_no,
                "Full Name": s.full_name,
                "Branch": s.branch,
                "Branch Code": s.branch_code,
                "CGPA": ac.ug_cgpa if ac else None,
                "Passing Year": ac.ug_year_of_passing if ac else None,
                "Backlogs": ac.number_of_backlogs if ac else 0,
                "CRT Registered": ac.crt_registered if ac else "N",
                "Contact": phone_val,
                "Email": ct.recorded_email if ct else None,
                "Date of Birth": dob_val,
                "Father Name": father_val,
                "Admission Type": ac.admission_type if ac else None,
            })
        return pd.DataFrame(data) if data else pd.DataFrame(columns=default_cols)

    elif report_type == "academic":
        students = db.query(Student).filter(Student.is_archived == False).all()
        data = []
        for s in students:
            ac = s.academics
            data.append({
                "Roll No": s.roll_no,
                "Full Name": s.full_name,
                "Branch": s.branch,
                "UG CGPA": ac.ug_cgpa if ac else None,
                "Backlogs": ac.number_of_backlogs if ac else 0,
                "10th Board": ac.x_grading_system if ac else None,
                "10th Marks/CGPA": ac.x_cgpa_percentage if ac else None,
                "10th School": ac.x_school_name if ac else None,
                "12th/Diploma": ac.study_after_x if ac else None,
                "12th Marks/CGPA": ac.xii_cgpa_percentage if ac else None,
                "12th College": ac.xii_college_name if ac else None,
            })
        return pd.DataFrame(data) if data else pd.DataFrame(columns=default_cols)

    elif report_type in ["internship", "organization_wise"]:
        internships = db.query(Internship).filter(Internship.is_deleted == False).all()
        data = [
            {
                "Roll No": i.roll_no,
                "Student Name": i.full_name,
                "Branch": i.branch,
                "Organization": i.name_of_organization,
                "District": i.organization_district,
                "Category": i.category,
                "Role": i.role,
                "Mode": i.mode_of_internship,
                "Type": i.internship_type,
                "Stipend (₹/mo)": i.stipend_amount,
                "Duration (Weeks)": i.duration_weeks,
                "Start Date": i.start_date.isoformat() if i.start_date else None,
                "End Date": i.end_date.isoformat() if i.end_date else None,
                "Certificate Received": i.certificate_received,
            }
            for i in internships
        ]
        return pd.DataFrame(data) if data else pd.DataFrame(columns=default_cols)

    elif report_type == "backlog":
        students = db.query(Student).join(StudentAcademic, StudentAcademic.student_id == Student.id).filter(
            Student.is_archived == False,
            StudentAcademic.number_of_backlogs > 0
        ).all()
        data = [
            {
                "Roll No": s.roll_no,
                "Full Name": s.full_name,
                "Branch": s.branch,
                "Backlogs Count": s.academics.number_of_backlogs if s.academics else 0,
                "CGPA": s.academics.ug_cgpa if s.academics else None,
                "Passing Year": s.academics.ug_year_of_passing if s.academics else None,
                "Contact": mask_phone(s.contacts.contact_number) if mask_sensitive and s.contacts else (s.contacts.contact_number if s.contacts else None),
            }
            for s in students
        ]
        return pd.DataFrame(data) if data else pd.DataFrame(columns=default_cols)

    elif report_type == "crt_registered":
        students = db.query(Student).join(StudentAcademic, StudentAcademic.student_id == Student.id).filter(
            Student.is_archived == False,
            StudentAcademic.crt_registered == "Y"
        ).all()
        data = [
            {
                "Roll No": s.roll_no,
                "Full Name": s.full_name,
                "Branch": s.branch,
                "CGPA": s.academics.ug_cgpa if s.academics else None,
                "Contact": mask_phone(s.contacts.contact_number) if mask_sensitive and s.contacts else (s.contacts.contact_number if s.contacts else None),
                "Placements Email": s.contacts.corrected_placement_email or s.contacts.recorded_email if s.contacts else None,
            }
            for s in students
        ]
        return pd.DataFrame(data) if data else pd.DataFrame(columns=default_cols)

    elif report_type == "without_internships":
        from sqlalchemy import select
        subquery = select(Internship.roll_no).filter(Internship.is_deleted == False).distinct()
        students = db.query(Student).filter(
            Student.is_archived == False,
            ~Student.roll_no.in_(subquery)
        ).all()
        data = [
            {
                "Roll No": s.roll_no,
                "Full Name": s.full_name,
                "Branch": s.branch,
                "CGPA": s.academics.ug_cgpa if s.academics else None,
                "Passing Year": s.academics.ug_year_of_passing if s.academics else None,
                "Contact": mask_phone(s.contacts.contact_number) if mask_sensitive and s.contacts else (s.contacts.contact_number if s.contacts else None),
            }
            for s in students
        ]
        return pd.DataFrame(data) if data else pd.DataFrame(columns=default_cols)

    elif report_type == "certificate_pending":
        internships = db.query(Internship).filter(
            Internship.is_deleted == False,
            (Internship.certificate_received == "No") | (Internship.certificate_received == None)
        ).all()
        data = [
            {
                "Roll No": i.roll_no,
                "Student Name": i.full_name,
                "Branch": i.branch,
                "Organization": i.name_of_organization,
                "Role": i.role,
                "End Date": i.end_date.isoformat() if i.end_date else None,
                "Certificate Received": "No",
            }
            for i in internships
        ]
        return pd.DataFrame(data) if data else pd.DataFrame(columns=default_cols)

    else:
        students = db.query(Student).filter(Student.is_archived == False).limit(100).all()
        data = [{"Roll No": s.roll_no, "Name": s.full_name, "Branch": s.branch} for s in students]
        return pd.DataFrame(data) if data else pd.DataFrame(columns=["Roll No", "Name", "Branch"])

def export_report_excel(df: pd.DataFrame, report_title: str) -> bytes:
    output = io.BytesIO()
    sheet_name = (report_title or "Report")[:30]
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        ws = writer.sheets[sheet_name]
        ws.freeze_panes = "A2"

        from openpyxl.styles import Font, PatternFill, Alignment
        header_fill = PatternFill(start_color="1D1D1F", end_color="1D1D1F", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        for col_idx, col_name in enumerate(df.columns, start=1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="left", vertical="center")

            max_len = len(str(col_name))
            if not df.empty:
                col_vals = df[col_name].dropna().astype(str)
                if not col_vals.empty:
                    max_len = max(max_len, int(col_vals.str.len().max()))
            col_letter = ws.cell(row=1, column=col_idx).column_letter
            ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 42)
    return output.getvalue()

def export_report_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def _draw_pdf_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#E5E7EB"))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 22, doc.pagesize[0] - doc.rightMargin, 22)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#6E6E73"))
    canvas.drawString(doc.leftMargin, 11, "Vignan's Institute Of Information Technology  •  Official Institutional Report")
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 11, f"Page {doc.page}")
    canvas.restoreState()

def export_report_pdf(df: pd.DataFrame, title: str) -> bytes:
    buffer = io.BytesIO()
    page_size = landscape(A4)
    margin_x = 24
    doc = SimpleDocTemplate(
        buffer,
        pagesize=page_size,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=24,
        bottomMargin=32,
    )
    styles = getSampleStyleSheet()

    eyebrow_style = ParagraphStyle(
        "ReportEyebrow",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0071E3"),
        spaceAfter=2,
    )
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#1D1D1F"),
        spaceAfter=3,
    )
    meta_style = ParagraphStyle(
        "ReportMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#6E6E73"),
    )
    header_cell_style = ParagraphStyle(
        "TableHeaderCell",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
    )
    body_cell_style = ParagraphStyle(
        "TableBodyCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor("#1D1D1F"),
    )
    empty_cell_style = ParagraphStyle(
        "TableEmptyCell",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#6E6E73"),
        alignment=1,
    )

    clean_title = html.escape(title.replace("_", " ").title())
    generated_at = datetime.now().strftime("%d %b %Y, %I:%M %p")
    total_rows = len(df)

    elements = [
        Paragraph("VIGNAN'S INSTITUTE OF INFORMATION TECHNOLOGY", eyebrow_style),
        Paragraph(f"{clean_title} Report", title_style),
        Paragraph(
            f"Generated: {generated_at}  &nbsp;|&nbsp;  Total Records: <b>{total_rows}</b>  &nbsp;|&nbsp;  Confidential Institutional Record",
            meta_style,
        ),
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB"), spaceAfter=12),
    ]

    cols = list(df.columns)[:10]
    usable_width = page_size[0] - (margin_x * 2)

    if not cols:
        cols = ["Status"]
        table_data = [
            [Paragraph("Status", header_cell_style)],
            [Paragraph("No records found", empty_cell_style)],
        ]
        col_widths = [usable_width]
    else:
        table_data = [[Paragraph(html.escape(str(c)), header_cell_style) for c in cols]]
        display_df = df.head(250)

        if display_df.empty:
            empty_row = [Paragraph("No matching records found.", empty_cell_style)] + [
                Paragraph("", body_cell_style) for _ in cols[1:]
            ]
            table_data.append(empty_row)
        else:
            for _, row in display_df.iterrows():
                table_data.append([
                    Paragraph(
                        html.escape(str(row[c]).strip()) if pd.notna(row[c]) and str(row[c]).strip() != "" else "—",
                        body_cell_style,
                    )
                    for c in cols
                ])

        # Compute proportional column widths so headers and values remain crisp and readable
        weights = []
        for c in cols:
            max_len = len(str(c))
            if not display_df.empty:
                vals = display_df[c].dropna().astype(str)
                if not vals.empty:
                    max_len = max(max_len, min(int(vals.str.len().quantile(0.9)), 28))
            weights.append(max(max_len, 7))
        total_weight = sum(weights) or 1
        col_widths = [(w / total_weight) * usable_width for w in weights]

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D1D1F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F7")]),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#1D1D1F")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
    ]
    if cols and df.empty:
        style_cmds.append(("SPAN", (0, 1), (-1, 1)))
    t.setStyle(TableStyle(style_cmds))

    elements.append(t)
    if len(df) > 250:
        elements.append(Spacer(1, 8))
        elements.append(
            Paragraph(
                f"Showing first 250 of {len(df)} records in PDF. Export Excel (.xlsx) or CSV for the complete dataset.",
                meta_style,
            )
        )

    doc.build(elements, onFirstPage=_draw_pdf_footer, onLaterPages=_draw_pdf_footer)
    return buffer.getvalue()
