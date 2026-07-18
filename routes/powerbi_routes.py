from flask import Blueprint
from services.powerbi_export_service import PowerBIExportService

powerbi_bp = Blueprint("powerbi", __name__)


from flask import Blueprint, redirect, url_for, flash
from services.powerbi_export_service import PowerBIExportService

powerbi_bp = Blueprint("powerbi", __name__)

@powerbi_bp.route("/powerbi/export")
def export_dataset():

    PowerBIExportService.export_all()

    flash("Power BI Dataset Generated Successfully!", "success")

    return redirect(url_for("admin_new.dashboard"))