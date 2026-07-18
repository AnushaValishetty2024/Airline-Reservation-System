-- ======================================
-- BOOKING ANALYTICS
-- ======================================


-- Total Bookings


SELECT 
COUNT(*) AS total_bookings

FROM bookings;



-- Booking Status Analysis


SELECT

bs.status_name,

COUNT(b.id) AS total

FROM bookings b


JOIN booking_status bs

ON b.booking_status_id=bs.id

GROUP BY bs.status;



-- Monthly Booking Trend


WITH booking_month AS

(

SELECT

DATE_FORMAT(created_at,'%Y-%m') month,

COUNT(id) bookings


FROM bookings


GROUP BY month

)


SELECT *

FROM booking_month

ORDER BY month;



-- Booking Ranking By Customer


SELECT


u.name,


COUNT(b.id) booking_count,


ROW_NUMBER() OVER(

ORDER BY COUNT(b.id) DESC

) ranking



FROM users u


JOIN bookings b

ON u.id=b.user_id


GROUP BY u.name;



-- Peak Booking Hours


SELECT


HOUR(created_at) booking_hour,

COUNT(*) total_bookings


FROM bookings


GROUP BY booking_hour


ORDER BY total_bookings DESC;