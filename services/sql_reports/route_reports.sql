-- =====================================
-- ROUTE PERFORMANCE
-- =====================================



-- Route Analysis


SELECT


CONCAT(
ao.city,
' - ',
ad.city
) route,


COUNT(b.id) bookings,


SUM(p.amount) revenue



FROM flights f



JOIN airports ao

ON f.origin_airport_id=ao.id



JOIN airports ad

ON f.destination_airport_id=ad.id



JOIN bookings b

ON f.id=b.flight_id



JOIN payments p

ON b.id=p.booking_id



GROUP BY route;



-- Popular Destination


SELECT


ad.city,


COUNT(b.id) passengers



FROM flights f


JOIN airports ad

ON f.destination_airport_id=ad.id


JOIN bookings b

ON f.id=b.flight_id


GROUP BY ad.city


ORDER BY passengers DESC;



-- Route Ranking


SELECT


route,


bookings,


RANK() OVER(

ORDER BY bookings DESC

) ranking


FROM

(

SELECT


CONCAT(
ao.city,'-',ad.city
) route,


COUNT(b.id) bookings


FROM flights f


JOIN airports ao

ON f.origin_airport_id=ao.id


JOIN airports ad

ON f.destination_airport_id=ad.id


JOIN bookings b

ON f.id=b.flight_id


GROUP BY route


)t;