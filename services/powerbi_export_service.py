import os
import pandas as pd
from models.db import get_db_connection


class PowerBIExportService:

    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    EXPORT_FOLDER = os.path.join(BASE_DIR, "powerbi_dataset")

    @staticmethod
    def ensure_folder():
        if not os.path.exists(PowerBIExportService.EXPORT_FOLDER):
            os.makedirs(PowerBIExportService.EXPORT_FOLDER)

    @staticmethod
    def export_csv(filename, query):

        print(f"\nStarting export: {filename}")

        PowerBIExportService.ensure_folder()

        conn = None

        try:
            conn = get_db_connection()

            print("Database connected")

            df = pd.read_sql(query, conn)

            print(f"Rows fetched: {len(df)}")

            filepath = os.path.join(
                PowerBIExportService.EXPORT_FOLDER,
                filename
            )

            df.to_csv(filepath, index=False)

            print(f"Saved: {filepath}")

            return filepath

        except Exception:
            import traceback
            traceback.print_exc()
            return None

        finally:
            if conn:
                conn.close()

    @staticmethod
    def export_all():

        print("========== EXPORT STARTED ==========")

        PowerBIExportService.export_csv(
            "revenue_data.csv",
            "SELECT * FROM vw_revenue_summary"
        )

        PowerBIExportService.export_csv(
            "booking_data.csv",
            "SELECT * FROM vw_booking_summary"
        )

        PowerBIExportService.export_csv(
            "customer_data.csv",
            "SELECT * FROM vw_customer_summary"
        )

        PowerBIExportService.export_csv(
            "flight_data.csv",
            "SELECT * FROM vw_flight_performance"
        )

        PowerBIExportService.export_csv(
            "route_data.csv",
            "SELECT * FROM vw_route_performance"
        )

        print("========== EXPORT COMPLETED ==========")

        return True