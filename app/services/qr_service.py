import os
import secrets
import uuid

import qrcode

from app.core.config import settings


def generate_ticket_code() -> str:
    """Return a unique, human-friendly ticket code."""
    return f"SE-{uuid.uuid4().hex[:8].upper()}-{secrets.token_hex(2).upper()}"


def generate_qr_code(ticket_code: str, extra_data: str = "") -> str:
    """Generate a QR image for the ticket and return its public URL."""
    os.makedirs(settings.QRCODE_DIR, exist_ok=True)

    filename = f"{ticket_code}.png"
    file_path = os.path.join(settings.QRCODE_DIR, filename)

    payload = f"ticket_code={ticket_code}"
    if extra_data:
        payload = f"{payload}&{extra_data}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    image.save(file_path)

    return f"{settings.BASE_URL}/static/qrcodes/{filename}"
