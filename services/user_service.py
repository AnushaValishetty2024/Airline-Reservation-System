from werkzeug.security import generate_password_hash, check_password_hash

from repositories.user_repository import (
    create_user as db_create_user,
    get_user_by_email,
    get_user_by_id,
    get_role_by_name,
    update_password as db_update_password,
    update_user_profile as db_update_user_profile,
    get_all_users,
    toggle_user_status,
)
from core.validators import is_valid_email, is_valid_mobile, is_strong_password


def authenticate_user(email: str, password: str):
    """Authenticate user by email and password."""
    user = get_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def register_user(full_name: str, email: str, mobile_number: str, password: str) -> int:
    """Register a new user with validation."""
    errors = []
    if not full_name:
        raise ValueError("Full name is required.")
    if not email or not is_valid_email(email):
        raise ValueError("Please provide a valid email address.")
    if not mobile_number or not is_valid_mobile(mobile_number):
        raise ValueError("Please provide a valid mobile number.")
    if not password or not is_strong_password(password):
        raise ValueError("Password must be at least 8 characters and contain an uppercase letter and a number.")

    existing = get_user_by_email(email)
    if existing:
        raise ValueError("An account with this email already exists.")

    role = get_role_by_name("User")
    if not role:
        raise ValueError("User role not configured.")

    password_hash = generate_password_hash(password)
    user_id = db_create_user(full_name, email, mobile_number, password_hash, role["id"])
    return user_id


def update_user_profile(user_id: int, full_name: str, email: str, mobile_number: str):
    """Update user profile."""
    if not full_name:
        raise ValueError("Full name is required.")
    if not email or not is_valid_email(email):
        raise ValueError("Please provide a valid email address.")
    if len(mobile_number) != 10 or not mobile_number.isdigit():
        raise ValueError("Enter a valid 10-digit mobile number.")

    existing = get_user_by_email(email)
    if existing and existing["id"] != user_id:
        raise ValueError("Email already in use.")

    db_update_user_profile(user_id, full_name, email, mobile_number)


def change_password(user_id: int, new_password: str):
    """Change user password."""
    if not new_password or not is_strong_password(new_password):
        raise ValueError("Password must be at least 8 characters and contain an uppercase letter and a number.")

    password_hash = generate_password_hash(new_password)
    db_update_password(user_id, password_hash)


def get_all_users_service():
    """Get all users."""
    return get_all_users()


def toggle_user_status_service(user_id: int):
    """Toggle user active/inactive status."""
    return toggle_user_status(user_id)
