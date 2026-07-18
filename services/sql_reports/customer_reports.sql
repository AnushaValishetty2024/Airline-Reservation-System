-- =====================================
-- CUSTOMER ANALYTICS
-- =====================================


-- Customer Booking Summary


SELECT


u.full_name,

u.email,


COUNT(b.id) total_bookings,


SUM(p.amount) total_spent



FROM users u


JOIN bookings b

ON u.id=b.user_id


JOIN payments p

ON b.id=p.booking_id



GROUP BY u.id;



-- Top Customers


SELECT


u.full_name,


SUM(p.amount) spending



FROM users u


JOIN bookings b

ON u.id=b.user_id


JOIN payments p

ON b.id=p.booking_id



GROUP BY u.full_name


ORDER BY spending DESC



LIMIT 10;



-- Customer Ranking


SELECT


u.full_name,


COUNT(b.id) bookings,


RANK() OVER(

ORDER BY COUNT(b.id) DESC

) customer_rank



FROM users u


JOIN bookings b

ON u.id=b.user_id


GROUP BY u.full_name;