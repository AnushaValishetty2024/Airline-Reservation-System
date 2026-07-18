import random
import string


def generate_booking_reference():
    """Generate unique booking reference like BK123456."""
    return "BK" + "".join(random.choices(string.digits, k=6))


def generate_payment_reference():
    """Generate unique payment reference like PAY123456."""
    return "PAY" + "".join(random.choices(string.digits, k=6))