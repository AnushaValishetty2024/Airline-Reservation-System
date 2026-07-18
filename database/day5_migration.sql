-- Day 5 Migration: Add any missing columns and create SQL views
USE airline_reservation;

-- Add any missing columns if needed
-- (Based on existing schema, most columns already exist)

-- SQL Views for analytics
CREATE OR REPLACE VIEW vw_revenue_summary AS
SELECT 
    DATE(p.paid_at) AS revenue_date,
    COUNT(DISTINCT b.id) AS total_bookings,
    SUM(p.amount) AS total_revenue,
    AVG(p.amount) AS avg_ticket_price,
    a.airline_name,
    ap1.airport_code AS origin,
    ap2.airport_code AS destination
FROM payments p
JOIN bookings b ON p.booking_id = b.id
JOIN flights f ON b.flight_id = f.id
JOIN airlines a ON f.airline_id = a.id
JOIN airports ap1 ON f.origin_airport_id = ap1.id
JOIN airports ap2 ON f.destination_airport_id = ap2.id
WHERE p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
GROUP BY DATE(p.paid_at), a.airline_name, ap1.airport_code, ap2.airport_code;

CREATE OR REPLACE VIEW vw_booking_summary AS
SELECT 
    b.id,
    b.booking_reference,
    b.user_id,
    CONCAT(u.full_name) AS user_name,
    f.flight_number,
    a.airline_name,
    o.airport_code AS origin_code,
    d.airport_code AS destination_code,
    bs.status_name AS booking_status,
    b.total_amount,
    b.booked_at,
    COUNT(bp.id) AS passenger_count
FROM bookings b
JOIN users u ON b.user_id = u.id
JOIN flights f ON b.flight_id = f.id
JOIN airlines a ON f.airline_id = a.id
JOIN airports o ON f.origin_airport_id = o.id
JOIN airports d ON f.destination_airport_id = d.id
JOIN booking_status bs ON b.booking_status_id = bs.id
LEFT JOIN booking_passengers bp ON bp.booking_id = b.id
GROUP BY b.id, b.booking_reference, b.user_id, u.full_name, f.flight_number, 
         a.airline_name, o.airport_code, d.airport_code, bs.status_name, 
         b.total_amount, b.booked_at;

CREATE OR REPLACE VIEW vw_user_statistics AS
SELECT 
    u.id,
    u.full_name,
    u.email,
    u.created_at,
    COUNT(DISTINCT b.id) AS total_bookings,
    COALESCE(SUM(p.amount), 0) AS total_spent,
    MAX(b.booked_at) AS last_booking_date,
    MIN(b.booked_at) AS first_booking_date
FROM users u
LEFT JOIN bookings b ON b.user_id = u.id
LEFT JOIN payments p ON p.booking_id = b.id 
    AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
GROUP BY u.id, u.full_name, u.email, u.created_at;

CREATE OR REPLACE VIEW vw_flight_statistics AS
SELECT 
    f.id,
    f.flight_number,
    a.airline_name,
    o.airport_code AS origin_code,
    d.airport_code AS destination_code,
    f.departure_datetime,
    f.arrival_datetime,
    COUNT(DISTINCT b.id) AS total_bookings,
    COUNT(bp.id) AS booked_seats,
    f.seats_economy + f.seats_business AS total_seats,
    ROUND((COUNT(bp.id) / (f.seats_economy + f.seats_business)) * 100, 2) AS occupancy_percentage,
    COALESCE(SUM(p.amount), 0) AS total_revenue
FROM flights f
JOIN airlines a ON f.airline_id = a.id
JOIN airports o ON f.origin_airport_id = o.id
JOIN airports d ON f.destination_airport_id = d.id
LEFT JOIN bookings b ON b.flight_id = f.id
LEFT JOIN booking_passengers bp ON bp.booking_id = b.id
LEFT JOIN payments p ON p.booking_id = b.id 
    AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
GROUP BY f.id, f.flight_number, a.airline_name, o.airport_code, d.airport_code, 
         f.departure_datetime, f.arrival_datetime, f.seats_economy, f.seats_business;

CREATE OR REPLACE VIEW vw_route_statistics AS
SELECT 
    CONCAT(o.airport_code, ' → ', d.airport_code) AS route_name,
    o.city AS origin_city,
    d.city AS destination_city,
    COUNT(DISTINCT f.id) AS total_flights,
    COUNT(DISTINCT b.id) AS total_bookings,
    COALESCE(SUM(p.amount), 0) AS total_revenue
FROM flights f
JOIN airports o ON f.origin_airport_id = o.id
JOIN airports d ON f.destination_airport_id = d.id
LEFT JOIN bookings b ON b.flight_id = f.id
LEFT JOIN payments p ON p.booking_id = b.id 
    AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
GROUP BY o.airport_code, d.airport_code, o.city, d.city;