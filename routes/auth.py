from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.user_service import (
    authenticate_user,
    register_user,
    change_password,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        mobile_number = request.form.get("mobile_number", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("register.html", full_name=full_name, email=email, mobile_number=mobile_number)

        try:
            register_user(full_name, email, mobile_number, password)
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except ValueError as e:
            flash(str(e), "danger")
            return render_template("register.html", full_name=full_name, email=email, mobile_number=mobile_number)

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") is not None

        user = authenticate_user(email, password)
        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["role_name"] = user["role_name"]
            if remember:
                session.permanent = True
            flash("Login successful.", "success")
            if user["role_name"] == "Admin":
                return redirect(url_for("admin_new.dashboard"))
            return redirect(url_for("user.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
