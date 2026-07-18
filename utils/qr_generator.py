import qrcode
import io
import base64


def generate_qr_code(data: str, size: int = 10) -> str:
    """
    Generate QR code and return as base64 encoded string.

    Args:
        data: Data to encode in QR code
        size: QR code size (1-40)

    Returns:
        base64 encoded PNG image string
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Encode to base64
        img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"

    except Exception as e:
        print(f"QR generation error: {e}")
        return None


def generate_booking_qr(booking_reference: str, booking_id: int) -> dict:
    """
    Generate QR code for booking.

    Args:
        booking_reference: Booking reference number
        booking_id: Booking ID

    Returns:
        dict with QR code data
    """
    qr_data = f"BOOKING:{booking_id}|REF:{booking_reference}"
    qr_image = generate_qr_code(qr_data, size=8)

    return {
        "success": True,
        "booking_reference": booking_reference,
        "booking_id": booking_id,
        "qr_data": qr_data,
        "qr_image": qr_image,
    }