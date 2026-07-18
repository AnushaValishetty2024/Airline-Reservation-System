import os
import pandas as pd
from models.db import get_db_connection


class ExportService:

    EXPORT_FOLDER = "exports"

    @staticmethod
    def ensure_folder():
        if not os.path.exists(ExportService.EXPORT_FOLDER):
            os.makedirs(ExportService.EXPORT_FOLDER)

    @staticmethod
    def export_revenue():
        ExportService.ensure_folder()

        conn = get_db_connection()

        query = """
        SELECT *
        FROM vw_revenue_summary
        """

        df = pd.read_sql(query, conn)

        path = os.path.join(
            ExportService.EXPORT_FOLDER,
            "revenue_report.csv"
        )

        df.to_csv(path, index=False)

        conn.close()

        return path

    @staticmethod
    def export_bookings():
        ExportService.ensure_folder()

        conn = get_db_connection()

        query = """
        SELECT *
        FROM vw_booking_summary
        """

        df = pd.read_sql(query, conn)

        path = os.path.join(
            ExportService.EXPORT_FOLDER,
            "booking_summary.csv"
        )

        df.to_csv(path, index=False)

        conn.close()

        return path

    @staticmethod
    def export_customers():
        ExportService.ensure_folder()

        conn = get_db_connection()

        query = """
        SELECT *
        FROM vw_customer_summary
        """

        df = pd.read_sql(query, conn)

        path = os.path.join(
            ExportService.EXPORT_FOLDER,
            "customer_summary.csv"
        )

        df.to_csv(path, index=False)

        conn.close()

        return path

    @staticmethod
    def export_flights():
        ExportService.ensure_folder()

        conn = get_db_connection()

        query = """
        SELECT *
        FROM vw_flight_performance
        """

        df = pd.read_sql(query, conn)

        path = os.path.join(
            ExportService.EXPORT_FOLDER,
            "flight_performance.csv"
        )

        df.to_csv(path, index=False)

        conn.close()

        return path