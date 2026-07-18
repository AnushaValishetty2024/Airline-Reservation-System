from models.user import get_db_connection



class CustomerAnalyticsService:


    def get_total_customers(self):

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT COUNT(*) 
        FROM users
        """

        cursor.execute(query)

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result[0]



    def get_active_customers(self):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        query = """

        SELECT COUNT(DISTINCT user_id) AS active
        FROM bookings
        WHERE booking_status_id IN
        (
            SELECT id 
            FROM booking_status
            WHERE status_name IN ('Confirmed','Completed')
        )

        """


        cursor.execute(query)

        result = cursor.fetchone()

        cursor.close()
        conn.close()


        return result["active"]




    def get_top_customers(self):

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)


        query = """

        SELECT 
    u.full_name AS name,
    COUNT(b.id) AS total_bookings,
    SUM(p.amount) AS spending


        FROM users u


        JOIN bookings b
        ON u.id=b.user_id


        JOIN payments p
        ON b.id=p.booking_id


        GROUP BY u.id


        ORDER BY spending DESC


        LIMIT 10

        """


        cursor.execute(query)


        data = cursor.fetchall()


        cursor.close()
        conn.close()


        return data





    def get_booking_frequency(self):

        conn=get_db_connection()

        cursor=conn.cursor(dictionary=True)


        query="""

        SELECT

u.full_name AS name,

COUNT(b.id) AS bookings


        FROM users u


        JOIN bookings b

        ON u.id=b.user_id


        GROUP BY u.id


        ORDER BY bookings DESC


        LIMIT 10


        """


        cursor.execute(query)


        data=cursor.fetchall()


        cursor.close()
        conn.close()


        return data




    def get_customer_spending(self):

        conn=get_db_connection()

        cursor=conn.cursor()


        query="""

        SELECT 
        SUM(amount)

        FROM payments

        WHERE payment_status_id=1

        """


        cursor.execute(query)


        result=cursor.fetchone()


        cursor.close()
        conn.close()


        return result[0] or 0
    