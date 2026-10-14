from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------
# SKILLCIETY ORANGE & GREEN COLOR THEME
# ---------------------------------------------

ORANGE = colors.HexColor("#E87524")
GREEN = colors.HexColor("#168052")
LIGHT_GREEN = colors.HexColor("#DDF5E7")
LIGHT_GREY = colors.HexColor("#F3F5F8")
TEXT_GREY = colors.HexColor("#475569")
DARK_TEXT = colors.HexColor("#172033")


def generate_fee_receipt(
    institute_name,
    student_name,
    student_id,
    receipt_number,
    fee_month,
    payment_date,
    amount_paid,
    student_class="",
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
        title=f"Fee Receipt - {receipt_number}",
    )

    styles = getSampleStyleSheet()

    # Large SKILLCIETY heading
    title_style = ParagraphStyle(
        "ReceiptTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=colors.white,
        alignment=TA_CENTER,
    )

    # Smaller STUDENT FEE RECEIPT heading
    institute_style = ParagraphStyle(
        "InstituteName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.white,
        alignment=TA_CENTER,
    )

    label_style = ParagraphStyle(
        "ReceiptLabel",
        parent=styles["Normal"],
        fontSize=10,
        textColor=TEXT_GREY,
    )

    value_style = ParagraphStyle(
        "ReceiptValue",
        parent=styles["Normal"],
        fontSize=10,
        textColor=DARK_TEXT,
    )

    amount_style = ParagraphStyle(
        "ReceiptAmount",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=19,
        textColor=GREEN,
        alignment=TA_CENTER,
    )

    story = []

    # ---------------------------------------------
    # ORANGE HEADER WITH SWAPPED HEADINGS
    # ---------------------------------------------

    header = Table(
        [
            [Paragraph("SKILLCIETY", title_style)],
            [
                Paragraph(
                    "STUDENT FEE RECEIPT",
                    institute_style,
                )
            ],
        ],
        colWidths=[166 * mm],
    )

    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), ORANGE),
                ("TOPPADDING", (0, 0), (-1, 0), 16),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 1), (-1, 1), 4),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 16),
            ]
        )
    )

    story.append(header)
    story.append(Spacer(1, 12 * mm))

    # Receipt number
    receipt_info = Table(
        [
            [
                Paragraph("<b>Receipt No.</b>", label_style),
                Paragraph(
                    escape(str(receipt_number)),
                    value_style,
                ),
            ]
        ],
        colWidths=[83 * mm, 83 * mm],
    )

    receipt_info.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#CBD5E1"),
                ),
            ]
        )
    )

    story.append(receipt_info)
    story.append(Spacer(1, 7 * mm))

    # Student and payment details
    details = [
    ("Student Name", student_name),
    ("Student ID", student_id),
    ("Class", student_class),
    ("Fee Month", fee_month),
    ("Payment Date", payment_date),
]

    detail_rows = [
        [
            Paragraph(label, label_style),
            Paragraph(escape(str(value)), value_style),
        ]
        for label, value in details
    ]

    detail_table = Table(
        detail_rows,
        colWidths=[65 * mm, 101 * mm],
        rowHeights=[15 * mm] * len(detail_rows),
    )

    detail_table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#E2E8F0"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#E2E8F0"),
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(detail_table)
    story.append(Spacer(1, 12 * mm))

    # Amount paid
    amount_table = Table(
        [
            [
                Paragraph("<b>Amount Paid</b>", value_style),
                Paragraph(
                    f"Rs. {float(amount_paid):,.2f}",
                    amount_style,
                ),
            ]
        ],
        colWidths=[83 * mm, 83 * mm],
    )

    amount_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#CBD5E1"),
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(amount_table)
    story.append(Spacer(1, 7 * mm))

    # Green payment confirmation
    status_style = ParagraphStyle(
        "PaymentStatus",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=GREEN,
        alignment=TA_CENTER,
    )

    status = Table(
        [[Paragraph("PAYMENT RECEIVED", status_style)]],
        colWidths=[166 * mm],
    )

    status.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )

    story.append(status)
    story.append(Spacer(1, 15 * mm))

    # Footer
    footer_style = ParagraphStyle(
        "ReceiptFooter",
        parent=styles["Normal"],
        fontSize=10,
        textColor=TEXT_GREY,
        alignment=TA_CENTER,
    )

    story.append(
        Paragraph(
            "Thank you for your payment.",
            footer_style,
        )
    )

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes