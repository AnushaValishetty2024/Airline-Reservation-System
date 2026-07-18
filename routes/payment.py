import traceback
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, send_file
from flask import current_app
from io import BytesIO
import os
import traceback

from services.payment_service import process_payment, get_payment_details, get_payment_methods
from services.pricing_service import get_pricing_breakdown, calculate_dynamic_price
from services.ticket_service import create_ticket, get_ticket_path
from services.invoice_service import create_invoice, get_invoice_path
from services.notification_service import (
    notify_booking_confirmed,
    notify_payment_successful,
    notify_payment_failed,
    notify_ticket_generated,
    notify_invoice_generated,
)

payment_bp = Blueprint("payment", __name__)


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not getattr(g, "current_user", None):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


@payment_bp.route("/payment/<int:booking_id>", methods=["GET", "POST"])
@login_required
def payment_page(booking_id):
    payment_methods = []
    pricing_breakdown = None
    
    from services.booking_service import get_booking_details

    try:
        booking = get_booking_details(booking_id)
        if not booking:
            flash("Booking not found.", "danger")
            return redirect(url_for("user.booking_history"))

        # Ensure user can only access their own booking
        if booking["user_id"] != g.current_user["id"]:
            flash("Access denied.", "danger")
            return redirect(url_for("user.booking_history"))

        cabin_class = booking.get("cabin_class", "economy")

        passenger_count = booking.get("passenger_count", 1)
        # Get pricing breakdown
        pricing_breakdown = get_pricing_breakdown(
    booking["flight_id"],
    cabin_class,
    passenger_count
)
        if not pricing_breakdown.get("success"):
            flash("Error calculating fare breakdown.", "warning")
            pricing_breakdown = {
    "success": True,
    "base_fare": float(booking["total_amount"]),
    "taxes": 0.00,
    "gst": 0.00,
    "convenience_fee": 0.00,
    "grand_total": float(booking["total_amount"])
}
        if request.method == "POST":
            payment_method = request.form.get("payment_method", "").strip()
            if not payment_method:
                flash("Please select a payment method.", "warning")
                return redirect(url_for("payment.payment_page", booking_id=booking_id))
            amount = pricing_breakdown.get("grand_total", booking["total_amount"])

            if booking.get("payment_status") == "Paid":
              flash("This booking has already been paid.", "info")
              return redirect(
              url_for("payment.payment_success", booking_id=booking_id)
    )

            try:
                result = process_payment(booking_id, amount, payment_method)
                print("Payment Result:", result)

                if result.get("success"):
                    # Payment successful - generate ticket and invoice
                    ticket_result = create_ticket(booking_id)
                    invoice_result = create_invoice(booking_id)

                    # Create notifications
                    notify_payment_successful(
                        g.current_user["id"],
                        booking["booking_reference"],
                        float(amount),
                        result.get("transaction_id", "N/A")
                    )

                    if ticket_result.get("success"):
                        notify_ticket_generated(
                            g.current_user["id"],
                            booking["booking_reference"]
                        )
                    
                    if invoice_result.get("success"):
                        notify_invoice_generated(
                            g.current_user["id"],
                            booking["booking_reference"],
                            invoice_result.get("invoice_number", ""),
                            float(amount)
                        )

                    flash("Payment successful! Your ticket and invoice have been generated.", "success")
                    return redirect(url_for("payment.payment_success", booking_id=booking_id))

                else:
                    # Payment failed
                    error_msg = result.get("error", "Payment processing failed")
                    notify_payment_failed(
                        g.current_user["id"],
                        booking["booking_reference"],
                        error_msg
                    )
                    flash(f"Payment failed: {error_msg}", "danger")
                    return redirect(url_for("payment.payment_failed", booking_id=booking_id))

            except ValueError as e:
               flash(str(e), "danger")

            except Exception as e:
                 traceback.print_exc()
                 flash(f"Payment error: {e}", "danger")
# Load payment methods
        payment_methods = get_payment_methods()

        
 
        return render_template(
            "payment.html",
            page_title="Payment",
            booking=booking,
            pricing=pricing_breakdown,
            payment_methods=payment_methods,
        )

    except Exception as e:
        traceback.print_exc()
        flash(f"Error loading payment page: {e}", "danger")
        return redirect(url_for("user.booking_history"))

@payment_bp.route("/payment/process", methods=["POST"])
@login_required
def process_payment_route():
    """Process payment via AJAX or form POST."""
    import json

    try:
        booking_id = request.form.get("booking_id", type=int)
        payment_method = request.form.get("payment_method", "").strip()

        if not booking_id or not payment_method:
            return {"success": False, "error": "Missing booking_id or payment_method"}, 400

        # Get booking
        
        from services.booking_service import get_booking_details

        booking = get_booking_details(booking_id)
        if not booking or booking["user_id"] != g.current_user["id"]:
            return {"success": False, "error": "Invalid booking"}, 404

        # Get amount
        pricing_breakdown = get_pricing_breakdown(
    booking["flight_id"],
    "economy",
    1
)
        amount = pricing_breakdown.get("grand_total", booking["total_amount"]) if pricing_breakdown.get("success") else booking["total_amount"]

        # Process payment
        result = process_payment(booking_id, amount, payment_method)

        return result, 200

    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@payment_bp.route("/payment/success/<int:booking_id>")
@login_required
def payment_success(booking_id):
    
    from services.booking_service import get_booking_details
    from services.notification_service import notify_booking_confirmed

    try:
        booking = get_booking_details(booking_id)
        if not booking or booking["user_id"] != g.current_user["id"]:
            flash("Invalid booking.", "danger")
            return redirect(url_for("user.booking_history"))

        # Notify booking confirmed (only if not already notified)
        # This is a simplified check - in production you'd track this better
        # notify_booking_confirmed(g.current_user["id"], booking["booking_reference"], booking["flight_number"])

        # Get ticket and invoice paths
        ticket_path = get_ticket_path(booking_id)
        invoice_path = get_invoice_path(booking_id)

        return render_template(
            "payment_success.html",
            page_title="Payment Successful",
            booking=booking,
            ticket_path=ticket_path,
            invoice_path=invoice_path,
        )

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("user.booking_history"))


@payment_bp.route("/payment/failure/<int:booking_id>")
@login_required
def payment_failed(booking_id):
    from services.booking_service import get_booking_details

    try:
        booking = get_booking_details(booking_id)
        if not booking or booking["user_id"] != g.current_user["id"]:
            flash("Invalid booking.", "danger")
            return redirect(url_for("user.booking_history"))

        return render_template(
            "payment_failed.html",
            page_title="Payment Failed",
            booking=booking,
        )

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("user.booking_history"))


@payment_bp.route("/ticket/<int:booking_id>")
@login_required
def download_ticket(booking_id):
    """Download ticket PDF. Auto-generate if missing for completed payments."""
    from services.booking_service import get_booking_details

    try:
        booking = get_booking_details(booking_id)
        if not booking or booking["user_id"] != g.current_user["id"]:
            flash("Invalid booking.", "danger")
            return redirect(url_for("user.booking_history"))

        ticket_path = get_ticket_path(booking_id)
        if not ticket_path or not os.path.exists(ticket_path):
            # Auto-generate ticket if missing (for legacy bookings with completed payments)
            from services.ticket_service import create_ticket
            ticket_result = create_ticket(booking_id)
            if not ticket_result.get("success"):
                flash(f"Failed to generate ticket: {ticket_result.get('error')}", "warning")
                return redirect(url_for("user.booking_history"))
            ticket_path = get_ticket_path(booking_id)

        if not ticket_path or not os.path.exists(ticket_path):
            flash("Ticket not found. Please contact support.", "warning")
            return redirect(url_for("user.booking_history"))

        return send_file(ticket_path, as_attachment=True, download_name=os.path.basename(ticket_path))

    except Exception as e:
        flash(f"Error downloading ticket: {str(e)}", "danger")
        return redirect(url_for("user.booking_history"))


@payment_bp.route("/invoice/<int:booking_id>")
@login_required
def download_invoice(booking_id):
    """Download invoice PDF. Auto-generate if missing for completed payments."""
    from services.booking_service import get_booking_details

    try:
        booking = get_booking_details(booking_id)
        if not booking or booking["user_id"] != g.current_user["id"]:
            flash("Invalid booking.", "danger")
            return redirect(url_for("user.booking_history"))

        invoice_path = get_invoice_path(booking_id)
        if not invoice_path or not os.path.exists(invoice_path):
            # Auto-generate invoice if missing (for legacy bookings with completed payments)
            from services.invoice_service import create_invoice
            invoice_result = create_invoice(booking_id)
            if not invoice_result.get("success"):
                flash(f"Failed to generate invoice: {invoice_result.get('error')}", "warning")
                return redirect(url_for("user.booking_history"))
            invoice_path = get_invoice_path(booking_id)

        if not invoice_path or not os.path.exists(invoice_path):
            flash("Invoice not found. Please contact support.", "warning")
            return redirect(url_for("user.booking_history"))

        return send_file(invoice_path, as_attachment=True, download_name=os.path.basename(invoice_path))

    except Exception as e:
        flash(f"Error downloading invoice: {str(e)}", "danger")
        return redirect(url_for("user.booking_history"))


@payment_bp.route("/notifications")
@login_required
def notifications_page():
    from services.notification_service import get_user_notifications, get_unread_count

    try:
        notifications = get_user_notifications(g.current_user["id"], limit=50)
        unread_count = get_unread_count(g.current_user["id"])

        return render_template(
            "notifications.html",
            page_title="Notifications",
            notifications=notifications,
            unread_count=unread_count,
        )
    except Exception as e:
    
        traceback.print_exc()
        print(f"Error loading notifications: {e}")
        return render_template(
            "notifications.html",
            page_title="Notifications",
            notifications=[],
            unread_count=0,
        )

@payment_bp.route("/notifications/mark-read/<int:notification_id>", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    from services.notification_service import mark_notification_as_read

    try:
        success = mark_notification_as_read(notification_id, g.current_user["id"])
        if success:
            flash("Notification marked as read.", "success")
        else:
            flash("Failed to mark notification as read.", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("payment.notifications_page"))


@payment_bp.route("/notifications/mark-all-read", methods=["POST"])
@login_required
def mark_all_notifications_read():
    from services.notification_service import mark_all_notifications_as_read

    try:
        success = mark_all_notifications_as_read(g.current_user["id"])
        if success:
            flash("All notifications marked as read.", "success")
        else:
            flash("Failed to mark notifications as read.", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("payment.notifications_page"))