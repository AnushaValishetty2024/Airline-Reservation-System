-- ======================================
-- REVENUE ANALYSIS REPORTS
-- ======================================


-- 1. Total Revenue

SELECT 
    SUM(p.amount) AS total_revenue
FROM payments p
WHERE p.payment_status_id = 2;



-- 2. Revenue By Airline
-- Complex JOIN

SELECT
    a.airline_name AS airline_name,
    SUM(p.amount) AS revenue
FROM payments p

JOIN bookings b
ON p.booking_id = b.id

JOIN flights f
ON b.flight_id = f.id

JOIN airlines a
ON f.airline_id = a.id

WHERE p.payment_status_id = 2

GROUP BY a.airline_name

ORDER BY revenue DESC;



-- 3. Monthly Revenue
-- CTE Query


WITH monthly_revenue AS (

SELECT
    DATE_FORMAT(p.paid_at,'%Y-%m') AS month,
    SUM(p.amount) AS revenue

FROM payments p

WHERE p.payment_status_id = 2

GROUP BY month

)


SELECT *
FROM monthly_revenue

ORDER BY month;



-- 4. Revenue Ranking
-- Window Function


SELECT

a.airline_name AS airline,

SUM(p.amount) AS revenue,


RANK() OVER(
ORDER BY SUM(p.amount) DESC
) AS revenue_rank


FROM payments p


JOIN bookings b
ON p.booking_id=b.id


JOIN flights f
ON b.flight_id=f.id


JOIN airlines a
ON f.airline_id=a.id


WHERE p.payment_status_id=2


GROUP BY a.nama.airline_namee;



-- 5. Create Revenue View


CREATE OR REPLACE VIEW revenue_summary AS

SELECT

a.airline_name AS airline,

COUNT(b.id) AS total_bookings,

SUM(p.amount) AS revenue


FROM airlines a


JOIN flights f
ON a.id=f.airline_id


JOIN bookings b
ON f.id=b.flight_id


JOIN payments p
ON b.id=p.booking_id


WHERE p.payment_status_id=2


GROUP BY a.airline_name;