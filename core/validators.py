import re


def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.fullmatch(pattern, email or ""))


def is_valid_mobile(mobile: str) -> bool:
    return bool(re.fullmatch(r"^[0-9+().-]{7,15}$", mobile or ""))


def is_strong_password(password: str) -> bool:
    return (
        len(password or "") >= 8
        and any(ch.isupper() for ch in password or "")
        and any(ch.isdigit() for ch in password or "")
    )