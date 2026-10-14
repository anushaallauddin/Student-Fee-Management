
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_student_statement(
    institute_name,
    student,
    payment_history,
    expected_fees,
    total_received,
    outstanding_balance,
):
    """Generate a PDF statement for one student's fee account."""

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    navy = colors.HexColor("#17365D")
    orange = colors.HexColor("#E87524")
    cream = colors.HexColor("#FFF5EA")
    light_gray = colors.HexColor("#F3F5F8")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "StatementTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=24,
        textColor=navy,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        "StatementNormal",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
    )

    story = []

    story.append(
        Paragraph(
            institute_name or "Student Fee Management",
            title_style,
        )
    )

    story.append(
        Paragraph("STUDENT FEE STATEMENT", title_style)
    )

    story.append(Spacer(1, 16))

    student_details = [
        ["Student ID", str(student.get("id", "-")),
         "Student Name", str(student.get("name") or "-")],
        ["Class / Course", str(student.get("subject") or "-"),
         "Monthly Fee", f"Rs. {float(student.get('monthly_fee') or 0):,.2f}"],
        ["Admission Date", str(student.get("admission_date") or "-"),
         "Guardian", str(student.get("guardian_name") or "-")],
        ["Guardian Contact", str(student.get("guardian_contact") or "-"),
         "Statement Date", __import__("datetime").date.today().isoformat()],
    ]

    details_table = Table(
        student_details,
        colWidths=[1.05 * inch, 2.15 * inch, 1.05 * inch, 2.25 * inch],
    )

    details_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), cream),
            ("BACKGROUND", (2, 0), (2, -1), cream),
            ("TEXTCOLOR", (0, 0), (0, -1), navy),
            ("TEXTCOLOR", (2, 0), (2, -1), navy),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9DEE7")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    story.append(details_table)
    story.append(Spacer(1, 18))

    story.append(
        Paragraph("FEE SUMMARY", styles["Heading2"])
    )

    summary_data = [
        ["Expected Fees", "Total Received", "Outstanding Balance"],
        [
            f"Rs. {expected_fees:,.2f}",
            f"Rs. {total_received:,.2f}",
            f"Rs. {outstanding_balance:,.2f}",
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[2.15 * inch, 2.15 * inch, 2.15 * inch],
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, 1), light_gray),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ])
    )

    story.append(summary_table)
    story.append(Spacer(1, 18))

    story.append(
        Paragraph("PAYMENT HISTORY", styles["Heading2"])
    )

    history_data = [
        ["Month", "Year", "Payment Date", "Amount (Rs.)", "Status"]
    ]

    monthly_fee = float(student.get("monthly_fee") or 0)

    for payment in payment_history:
        amount = float(payment.get("amount") or 0)

        if monthly_fee > 0 and amount >= monthly_fee:
            status = "Paid"
        elif amount > 0:
            status = "Partial"
        else:
            status = "Recorded"

        history_data.append([
            str(payment.get("month") or "-"),
            str(payment.get("year") or "-"),
            str(payment.get("payment_date") or "-"),
            f"{amount:,.2f}",
            status,
        ])

    if len(history_data) == 1:
        history_data.append(["No payments recorded", "", "", "", ""])

    history_table = Table(
        history_data,
        colWidths=[
            1.15 * inch,
            0.65 * inch,
            1.45 * inch,
            1.35 * inch,
            1.1 * inch,
        ],
        repeatRows=1,
    )

    history_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9DEE7")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_gray]),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(history_table)
    story.append(Spacer(1, 22))

    story.append(
        Paragraph(
            "This statement summarizes the fee records available "
            "in the Student Fee Management system. Please contact "
            "the institute if you notice any discrepancy.",
            normal_style,
        )
    )

    doc.build(story)

    buffer.seek(0)
    return buffer.getvalue()
