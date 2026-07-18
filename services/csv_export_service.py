import csv
import os
from datetime import datetime
from models.db import get_db_connection


EXPORT_FOLDER = "exports"


class CSVExporter:


    def __init__(self):

        if not os.path.exists(EXPORT_FOLDER):
            os.makedirs(EXPORT_FOLDER)



    def export_revenue_report(self):

        file_path = os.path.join(
            EXPORT_FOLDER,
            "revenue_report.csv"
        )


        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        query = """
        SELECT
            DATE(paid_at) AS date,
            SUM(amount) AS revenue,
            COUNT(*) AS payments
        FROM payments
        WHERE payment_status_id = 1
        GROUP BY DATE(paid_at)
        ORDER BY date;
        """


        cursor.execute(query)

        data = cursor.fetchall()


        with open(file_path,"w",newline="") as file:

            writer = csv.DictWriter(
                file,
                fieldnames=data[0].keys()
                if data else []
            )

            writer.writeheader()
            writer.writerows(data)


        cursor.close()
        conn.close()


        return file_path




    def export_booking_report(self):

        file_path = os.path.join(
            EXPORT_FOLDER,
            "booking_trends.csv"
        )


        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)


        query="""
        SELECT
            DATE(created_at) booking_date,
            COUNT(*) total_bookings
        FROM bookings
        GROUP BY DATE(created_at)
        ORDER BY booking_date;
        """


        cursor.execute(query)

        data=cursor.fetchall()


        with open(file_path,"w",newline="") as file:

            writer=csv.DictWriter(
                file,
                fieldnames=data[0].keys()
                if data else []
            )

            writer.writeheader()
            writer.writerows(data)


        cursor.close()
        conn.close()


        return file_path





    def export_customer_report(self):

        file_path=os.path.join(
            EXPORT_FOLDER,
            "customer_analysis.csv"
        )


        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)


        query="""
        SELECT
            u.id,
            u.name,
            COUNT(b.id) total_bookings,
            SUM(b.total_amount) total_spent
        FROM users u
        LEFT JOIN bookings b
        ON u.id=b.user_id
        GROUP BY u.id;
        """


        cursor.execute(query)

        data=cursor.fetchall()



        with open(file_path,"w",newline="") as file:

            writer=csv.DictWriter(
                file,
                fieldnames=data[0].keys()
                if data else []
            )

            writer.writeheader()
            writer.writerows(data)



        cursor.close()
        conn.close()


        return file_path




    def export_flight_performance(self):


        file_path=os.path.join(
            EXPORT_FOLDER,
            "flight_performance.csv"
        )


        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)


        query="""
        SELECT
            f.flight_number,
            a.name airline,
            COUNT(b.id) bookings
        FROM flights f
        JOIN airlines a
        ON f.airline_id=a.id
        LEFT JOIN bookings b
        ON f.id=b.flight_id
        GROUP BY f.id;
        """


        cursor.execute(query)

        data=cursor.fetchall()


        with open(file_path,"w",newline="") as file:

            writer=csv.DictWriter(
                file,
                fieldnames=data[0].keys()
                if data else []
            )

            writer.writeheader()
            writer.writerows(data)


        cursor.close()
        conn.close()


        return file_path





    def export_route_performance(self):


        file_path=os.path.join(
            EXPORT_FOLDER,
            "route_performance.csv"
        )


        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)


        query="""
        SELECT
            origin_airport_id,
            destination_airport_id,
            COUNT(*) total_bookings
        FROM bookings
        GROUP BY
            origin_airport_id,
            destination_airport_id;
        """


        cursor.execute(query)

        data=cursor.fetchall()


        with open(file_path,"w",newline="") as file:

            writer=csv.DictWriter(
                file,
                fieldnames=data[0].keys()
                if data else []
            )

            writer.writeheader()
            writer.writerows(data)


        cursor.close()
        conn.close()


        return file_path