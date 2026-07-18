-- =====================================
-- FLIGHT PERFORMANCE
-- =====================================



-- Flight Booking Count


SELECT


f.flight_number,


COUNT(b.id) total_bookings



FROM flights f


LEFT JOIN bookings b


ON f.id=b.flight_id


GROUP BY f.id;



-- Flight Revenue


SELECT


f.flight_number,


SUM(p.amount) revenue



FROM flights f


JOIN bookings b

ON f.id=b.flight_id


JOIN payments p

ON b.id=p.booking_id


GROUP BY f.flight_number;



-- Flight Ranking


SELECT


flight_number,


total_bookings,


RANK() OVER(

ORDER BY total_bookings DESC

) rank_position


FROM

(

SELECT


f.flight_number,


COUNT(b.id) total_bookings


FROM flights f


LEFT JOIN bookings b

ON f.id=b.flight_id


GROUP BY f.flight_number


)t;