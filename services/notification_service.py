from datetime import datetime

from models.user import get_db_connection


def create_notification(user_id: int, title: str, message: str, 
                        notification_type: str = "info") -> dict:
    """
    Create a new notification for a user.

    Args:
        user_id: User ID
        title: Notification title
        message: Notification message
        notification_type: Type (info, success, warning, error)

    Returns:
        dict with notification data
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            INSERT INTO notifications (user_id, title, message, notification_type, is_read, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, title, message, notification_type, 0, datetime.now())
        )
        notification_id = cursor.lastrowid
        conn.commit()

        return {
            "success": True,
            "notification_id": notification_id,
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "is_read": False,
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()


def get_user_notifications(user_id: int, limit: int = 50, 
                          include_read: bool = True) -> list:
    """
    Get notifications for a user.

    Args:
        user_id: User ID
        limit: Maximum number of notifications to return
        include_read: Whether to include read notifications

    Returns:
        List of notification dicts
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if include_read:
            cursor.execute(
                """
                SELECT id, user_id, title, message, notification_type, 
                       is_read, created_at
                FROM notifications
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit)
            )
        else:
            cursor.execute(
                """
                SELECT id, user_id, title, message, notification_type, 
                       is_read, created_at
                FROM notifications
                WHERE user_id = %s AND is_read = 0
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit)
            )

        notifications = cursor.fetchall()
        return notifications

    finally:
        cursor.close()
        conn.close()


def mark_notification_as_read(notification_id: int, user_id: int) -> bool:
    """
    Mark a notification as read.

    Args:
        notification_id: Notification ID
        user_id: User ID (for security)

    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE notifications 
            SET is_read = 1 
            WHERE id = %s AND user_id = %s
            """,
            (notification_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def mark_all_notifications_as_read(user_id: int) -> bool:
    """
    Mark all notifications as read for a user.

    Args:
        user_id: User ID

    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE notifications 
            SET is_read = 1 
            WHERE user_id = %s AND is_read = 0
            """,
            (user_id,)
        )
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_unread_count(user_id: int) -> int:
    """
    Get count of unread notifications for a user.

    Args:
        user_id: User ID

    Returns:
        Count of unread notifications
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM notifications
            WHERE user_id = %s AND is_read = 0
            """,
            (user_id,)
        )
        result = cursor.fetchone()
        return result["count"] if result else 0

    finally:
        cursor.close()
        conn.close()


def delete_notification(notification_id: int, user_id: int) -> bool:
    """
    Delete a notification.

    Args:
        notification_id: Notification ID
        user_id: User ID (for security)

    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM notifications 
            WHERE id = %s AND user_id = %s
            """,
            (notification_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


# Predefined notification creators for common events

def notify_booking_confirmed(user_id: int, booking_reference: str, 
                            flight_number: str) -> dict:
    """Create notification for booking confirmation."""
    title = "Booking Confirmed"
    message = f"Your booking {booking_reference} for flight {flight_number} has been confirmed."
    return create_notification(user_id, title, message, "success")


def notify_payment_successful(user_id: int, booking_reference: str, 
                             amount: float, transaction_id: str) -> dict:
    """Create notification for successful payment."""
    title = "Payment Successful"
    message = f"Payment of ${amount:.2f} for booking {booking_reference} completed. Transaction ID: {transaction_id}"
    return create_notification(user_id, title, message, "success")


def notify_ticket_generated(user_id: int, booking_reference: str) -> dict:
    """Create notification for ticket generation."""
    title = "Ticket Generated"
    message = f"Your ticket for booking {booking_reference} has been generated. You can download it from your booking history."
    return create_notification(user_id, title, message, "info")


def notify_invoice_generated(user_id: int, booking_reference: str, 
                            invoice_number: str, amount: float) -> dict:
    """Create notification for invoice generation."""
    title = "Invoice Generated"
    message = f"Invoice {invoice_number} for booking {booking_reference} (Amount: ${amount:.2f}) has been generated. You can download it from your booking history."
    return create_notification(user_id, title, message, "info")


def notify_flight_reminder(user_id: int, booking_reference: str, 
                          flight_number: str, departure_time: str) -> dict:
    """Create notification for flight reminder."""
    title = "Flight Reminder"
    message = f"Reminder: Your flight {flight_number} (Booking: {booking_reference}) departs at {departure_time}."
    return create_notification(user_id, title, message, "warning")


def notify_payment_failed(user_id: int, booking_reference: str, 
                         reason: str) -> dict:
    """Create notification for failed payment."""
    title = "Payment Failed"
    message = f"Payment for booking {booking_reference} failed. Reason: {reason}. Please try again."
    return create_notification(user_id, title, message, "error")


def notify_booking_cancelled(user_id: int, booking_reference: str) -> dict:
    """Create notification for booking cancellation."""
    title = "Booking Cancelled"
    message = f"Your booking {booking_reference} has been cancelled."
    return create_notification(user_id, title, message, "info")


def get_recent_notifications_summary(user_id: int, limit: int = 5) -> dict:
    """
    Get a summary of recent notifications.

    Args:
        user_id: User ID
        limit: Number of notifications to return

    Returns:
        dict with notifications and unread count
    """
    notifications = get_user_notifications(user_id, limit=limit)
    unread_count = get_unread_count(user_id)

    return {
        "notifications": notifications,
        "unread_count": unread_count,
        "total_returned": len(notifications),
    }