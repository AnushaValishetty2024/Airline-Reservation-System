from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os


def create_pdf_directory(directory: str):
    """Create directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)


def generate_pdf(filename: str, content_builder, output_dir: str = None) -> str:
    """
    Generate a PDF file.

    Args:
        filename: Name of the PDF file
        content_builder: Function that builds the PDF content (list of flowables)
        output_dir: Directory to save the PDF (default: tickets/)

    Returns:
        Full path of generated PDF
    """
    try:
        if output_dir is None:
            output_dir = "tickets"

        create_pdf_directory(output_dir)
        filepath = os.path.join(output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        content = content_builder()
        doc.build(content)

        return filepath

    except Exception as e:
        print(f"PDF generation error: {e}")
        return None


def get_styles():
    """Get custom styles for PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=colors.HexColor("#1a5490"),
        alignment=TA_CENTER,
        spaceAfter=30,
    ))

    styles.add(ParagraphStyle(
        name="CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1a5490"),
        spaceAfter=10,
    ))

    styles.add(ParagraphStyle(
        name="CustomBody",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="CustomCenter",
        parent=styles["BodyText"],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="Subtitle",
        parent=styles["BodyText"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=20,
    ))

    return styles


def build_ticket_content(booking_data: dict) -> list:
    """
    Build PDF ticket content.

    Args:
        booking_data: Dictionary with all ticket information

    Returns:
        List of flowables for the ticket PDF
    """
    styles = get_styles()
    story = []

    # Header with airline logo placeholder
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("✈ SKYLINE AIRLINES ✈", styles["CustomTitle"]))
    story.append(Paragraph("BOARDING PASS", styles["CustomTitle"]))
    story.append(Spacer(1, 0.2 * inch))

    # Decorative line
    story.append(Table([[""]], colWidths=[6 * inch], style=TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 2, colors.HexColor("#1a5490")),
        ("LINEBELOW", (0, 0), (-1, 0), 2, colors.HexColor("#1a5490")),
    ])))
    story.append(Spacer(1, 0.2 * inch))

    # Ticket Number
    if booking_data.get("ticket_number"):
        story.append(Paragraph(f"Ticket: {booking_data['ticket_number']}", styles["CustomCenter"]))
        story.append(Spacer(1, 0.1 * inch))

    # Flight Information Section
    story.append(Paragraph("FLIGHT INFORMATION", styles["CustomHeading"]))
    story.append(Spacer(1, 0.1 * inch))

    flight_data = [
        ["Booking Reference", booking_data.get("booking_reference", "")],
        ["Passenger Name", booking_data.get("passenger_name", "")],
        ["Flight Number", booking_data.get("flight_number", "")],
        ["Airline", booking_data.get("airline_name", "")],
        ["Departure", booking_data.get("origin_city", "")],
        ["Arrival", booking_data.get("destination_city", "")],
        ["Departure Time", booking_data.get("departure_time", "")],
        ["Arrival Time", booking_data.get("arrival_time", "")],
        ["Gate", booking_data.get("gate", "A1")],
        ["Boarding Time", booking_data.get("boarding_time", "")],
        ["Seat Number", booking_data.get("seat_number", "")],
        ["Class", booking_data.get("seat_class", "Economy")],
        ["Status", booking_data.get("booking_status", "Confirmed")],
    ]

    flight_table = Table(flight_data, colWidths=[2.5 * inch, 3.2 * inch])
    flight_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("PADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(flight_table)
    story.append(Spacer(1, 0.3 * inch))

    # QR Code Section
    story.append(Paragraph("BOARDING QR CODE", styles["CustomHeading"]))
    story.append(Spacer(1, 0.1 * inch))

    # Add QR code if available
    qr_image = booking_data.get("qr_image")
    if qr_image:
        try:
            import base64
            from io import BytesIO
            from PIL import Image as PILImage
            import tempfile

            # Decode base64 and create temporary file
            img_data = base64.b64decode(qr_image)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(img_data)
                tmp_path = tmp.name

            img = Image(tmp_path, width=2 * inch, height=2 * inch)
            story.append(img)
        except Exception as e:
            story.append(Paragraph(f"QR Code available at check-in", styles["CustomCenter"]))
    else:
        story.append(Paragraph("QR Code available at check-in", styles["CustomCenter"]))

    story.append(Spacer(1, 0.3 * inch))

    # Footer
    story.append(Table(
        [["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "|", "Skyline Airlines"]],
        colWidths=[1.5 * inch, 2 * inch, 0.5 * inch, 2 * inch],
        style=TableStyle([
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "LEFT"),
            ("ALIGN", (2, 0), (2, 0), "CENTER"),
            ("ALIGN", (3, 0), (3, 0), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#666666")),
        ])
    ))

    # Border around entire document
    story.append(Spacer(1, 0.2 * inch))
    story.append(Table([[""]], colWidths=[6 * inch], style=TableStyle([
        ("BOX", (0, 0), (-1, -1), 2, colors.HexColor("#1a5490")),
    ])))

    return story


def build_invoice_content(invoice_data: dict) -> list:
    """
    Build PDF invoice content.

    Args:
        invoice_data: Dictionary with all invoice information

    Returns:
        List of flowables for the invoice PDF
    """
    styles = get_styles()
    story = []

    # Header
    story.append(Spacer(1, 0.2 * inch))

    # Title
    story.append(Paragraph("INVOICE", styles["CustomTitle"]))
    story.append(Spacer(1, 0.2 * inch))

    # Invoice header info
    header_data = [
        ["Invoice Number:", invoice_data.get("invoice_number", "")],
        ["Date:", datetime.now().strftime("%Y-%m-%d")],
        ["Due Date:", "Due on receipt"],
    ]
    header_table = Table(header_data, colWidths=[2 * inch, 3 * inch])
    header_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3 * inch))

    # Customer Information
    story.append(Paragraph("BILL TO:", styles["CustomHeading"]))
    customer_data = [
        ["Name:", invoice_data.get("passenger_name", "")],
        ["Booking Reference:", invoice_data.get("booking_reference", "")],
        ["Payment Method:", invoice_data.get("payment_method", "")],
        ["Transaction ID:", invoice_data.get("transaction_id", "")],
    ]
    customer_table = Table(customer_data, colWidths=[2 * inch, 3 * inch])
    customer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 0.3 * inch))

    # Flight Details
    story.append(Paragraph("FLIGHT DETAILS", styles["CustomHeading"]))
    flight_data = [
        ["Flight Number:", invoice_data.get("flight_number", "")],
        ["Airline:", invoice_data.get("airline_name", "")],
        ["Route:", f"{invoice_data.get('origin_city', '')} to {invoice_data.get('destination_city', '')}"],
    ]
    flight_table = Table(flight_data, colWidths=[2 * inch, 3 * inch])
    flight_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(flight_table)
    story.append(Spacer(1, 0.3 * inch))

    # Fare Breakdown
    story.append(Paragraph("FARE BREAKDOWN", styles["CustomHeading"]))
    story.append(Spacer(1, 0.1 * inch))

    fare_data = [
        ["Description", "Amount"],
        ["Base Fare", f"${invoice_data.get('base_fare', 0):.2f}"],
        ["Taxes", f"${invoice_data.get('taxes', 0):.2f}"],
        ["GST", f"${invoice_data.get('gst', 0):.2f}"],
        ["Convenience Fee", f"${invoice_data.get('convenience_fee', 0):.2f}"],
    ]

    fare_table = Table(fare_data, colWidths=[3.5 * inch, 2 * inch])
    fare_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5490")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))

    story.append(fare_table)
    story.append(Spacer(1, 0.1 * inch))

    # Total
    total_data = [
        ["GRAND TOTAL", f"${invoice_data.get('grand_total', 0):.2f}"]
    ]
    total_table = Table(total_data, colWidths=[3.5 * inch, 2 * inch])
    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e8f4f8")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1a5490")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 14),
        ("PADDING", (0, 0), (-1, -1), 12),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1a5490")),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 0.2 * inch))

    # Payment Status
    payment_status = invoice_data.get("payment_status", "Completed")
    status_color = colors.HexColor("#28a745") if payment_status == "Completed" else colors.HexColor("#dc3545")

    story.append(Paragraph(f"Payment Status: {payment_status}", styles["CustomCenter"]))
    story.append(Spacer(1, 0.1 * inch))

    # Footer
    story.append(Table(
        [["Thank you for your booking!", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]],
        colWidths=[3.5 * inch, 2 * inch],
        style=TableStyle([
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#666666")),
        ])
    ))

    return story

def generate_ticket_pdf(booking_data: dict, filename: str = None):
    """
    Generate a ticket PDF.
    """
    if filename is None:
        booking_ref = booking_data.get("booking_reference", "ticket")
        filename = f"ticket_{booking_ref}.pdf"

    return generate_pdf(
        filename=filename,
        content_builder=lambda: build_ticket_content(booking_data),
        output_dir="tickets"
    )


def generate_invoice_pdf(invoice_data: dict, filename: str = None):
    """
    Generate an invoice PDF.
    """
    if filename is None:
        booking_ref = invoice_data.get("booking_reference", "invoice")
        filename = f"invoice_{booking_ref}.pdf"

    return generate_pdf(
        filename=filename,
        content_builder=lambda: build_invoice_content(invoice_data),
        output_dir="invoices"
    )