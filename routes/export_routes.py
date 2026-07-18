from flask import Blueprint, send_file

from services.export_service import ExportService

export_bp = Blueprint(
    "export",
    __name__,
    url_prefix="/exports"
)


@export_bp.route("/revenue")
def revenue():

    path = ExportService.export_revenue()

    return send_file(path, as_attachment=True)


@export_bp.route("/bookings")
def bookings():

    path = ExportService.export_bookings()

    return send_file(path, as_attachment=True)


@export_bp.route("/customers")
def customers():

    path = ExportService.export_customers()

    return send_file(path, as_attachment=True)


@export_bp.route("/flights")
def flights():

    path = ExportService.export_flights()

    return send_file(path, as_attachment=True)