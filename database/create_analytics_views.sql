-- Analytics Views for Day 6

-- Revenue Summary View
CREATE OR REPLACE VIEW vw_revenue_summary AS
SELECT 
    a.id AS airline_id,
    a.airline_name,
    a.airline_code,
    COUNT(DISTINCT b.id) AS total_bookings,
    COALESCE(SUM(p.amount), 0) AS total_revenue,
    COALESCE(AVG(p.amount), 0) AS avg_ticket_price,
    MIN(p.paid_at) AS first_booking_date,
    MAX(p.paid_at) AS last_booking_date
FROM airlines a
LEFT JOIN flights f ON a.id = f.airline_id
LEFT JOIN bookings b ON f.id = b.flight_id
LEFT JOIN payments p ON b.id = p.booking_id 
    AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
GROUP BY a.id, a.airline_name, a.airline_code;

-- Booking Summary View
CREATE OR REPLACE VIEW vw_booking_summary AS
SELECT 
    b.id,
    b.booking_reference,
    b.booked_at,
    bs.status_name AS booking_status,
    f.flight_number,
    a.airline_name,
    u.full_name AS customer_name,
    u.email AS customer_email,
    COUNT(bp.id) AS passenger_count,
    b.total_amount,
    COALESCE(SUM(p.amount), 0) AS paid_amount
FROM bookings b
JOIN booking_status bs ON b.booking_status_id = bs.id
JOIN flights f ON b.flight_id = f.id
JOIN airlines a ON f.airline_id = a.id
JOIN users u ON b.user_id = u.id
LEFT JOIN booking_passengers bp ON bp.booking_id = b.id
LEFT JOIN payments p ON p.booking_id = b.id
GROUP BY b.id, b.booking_reference, b.booked_at, bs.status_name, 
         f.flight_number, a.airline_name, u.full_name, u.email, b.total_amount;

-- Customer Summary View
CREATE OR REPLACE VIEW vw_customer_summary AS
SELECT 
    u.id AS user_id,
    u.full_name,
    u.email,
    u.mobile_number,
    u.created_at AS registration_date,
    COUNT(DISTINCT b.id) AS total_bookings,
    COALESCE(SUM(p.amount), 0) AS total_spent,
    COALESCE(AVG(p.amount), 0) AS avg_booking_value,
    MIN(b.booked_at) AS first_booking_date,
    MAX(b.booked_at) AS last_booking_date
FROM users u
LEFT JOIN bookings b ON u.id = b.user_id
LEFT JOIN payments p ON b.id = p.booking_id 
    AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
GROUP BY u.id, u.full_name, u.email, u.mobile_number, u.created_at;

-- Route Performance View
CREATE OR REPLACE VIEW vw_route_performance AS
SELECT 
    f.id AS flight_id,
    f.flight_number,
    a.airline_name,
    ap1.airport_code AS origin_code,
    ap1.city AS origin_city,
    ap2.airport_code AS destination_code,
    ap2.city AS destination_city,
    CONCAT(ap1.airport_code, ' -> ', ap2.airport_code) AS route_name,
    f.seats_economy + f.seats_business AS total_seats,
    COUNT(DISTINCT b.id) AS total_bookings,
    COUNT(bp.id) AS seats_sold,
    ROUND((COUNT(bp.id) / (f.seats_economy + f.seats_business)) * 100, 2) AS occupancy_rate,
    COALESCE(SUM(p.amount), 0) AS total_revenue
FROM flights f
JOIN airlines a ON f.airline_id = a.id
JOIN airports ap1 ON f.origin_airport_id = ap1.id
JOIN airports ap2 ON f.destination_airport_id = ap2.id
LEFT JOIN bookings b ON f.id = b.flight_id
LEFT JOIN booking_passengers bp ON b.id = bp.booking_id
LEFT JOIN payments p ON b.id = p.booking_id 
    AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
GROUP BY f.id, f.flight_number, a.airline_name, ap1.airport_code, ap1.city, 
         ap2.airport_code, ap2.city, f.seats_economy, f.seats_business;

-- Flight Performance View
CREATE OR REPLACE VIEW vw_flight_performance AS
SELECT 
    f.id,
    f.flight_number,
    a.airline_name,
    ac.aircraft_model,
    f.departure_datetime,
    f.arrival_datetime,
    f.status,
    f.seats_economy + f.seats_business AS total_capacity,
    COUNT(DISTINCT CASE WHEN bs.status_name IN ('Confirmed', 'Completed') THEN b.id END) AS confirmed_bookings,
    COUNT(DISTINCT b.id) AS total_bookings,
    COALESCE(SUM(p.amount), 0) AS total_revenue,
    ROUND((COUNT(bp.id) / (f.seats_economy + f.seats_business)) * 100, 2) AS occupancy_rate
FROM flights f
JOIN airlines a ON f.airline_id = a.id
JOIN aircraft ac ON f.aircraft_id = ac.id
LEFT JOIN bookings b ON f.id = b.flight_id
LEFT JOIN booking_status bs ON b.booking_status_id = bs.id
LEFT JOIN booking_passengers bp ON b.id = bp.booking_id
LEFT JOIN payments p ON b.id = p.booking_id 
    AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
GROUP BY f.id, f.flight_number, a.airline_name, ac.aircraft_model, 
         f.departure_datetime, f.arrival_datetime, f.status, f.seats_economy, f.seats_business;

-- Payment Summary View
CREATE OR REPLACE VIEW vw_payment_summary AS
SELECT 
    DATE(paid_at) AS payment_date,
    payment_method,
    ps.status_name AS payment_status,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount
FROM payments p
JOIN payment_status ps ON p.payment_status_id = ps.id
GROUP BY DATE(paid_at), payment_method, ps.status_name;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_bookings_status_date ON bookings(booking_status_id, booked_at);
CREATE INDEX IF NOT EXISTS idx_payments_date_status ON payments(paid_at, payment_status_id);
CREATE INDEX IF NOT EXISTS idx_flights_datetime ON flights(departure_datetime, status);
CREATE INDEX IF NOT EXISTS idx_bookings_flight ON bookings(flight_id);
CREATE INDEX IF NOT EXISTS idx_payments_amount ON payments(amount);
CREATE INDEX IF NOT EXISTS idx_bookings_amount ON bookings(total_amount);
CREATE INDEX IF NOT EXISTS idx_bookings_user_date ON bookings(user_id, booked_at);
CREATE INDEX IF NOT EXISTS idx_bookings_booking_date_status ON bookings(booked_at, booking_status_id);
CREATE INDEX IF NOT EXISTS idx_payments_booking_date ON payments(booking_id, paid_at);
CREATE INDEX IF NOT EXISTS idx_payments_status_date ON payments(payment_status_id, paid_at);
CREATE INDEX IF NOT EXISTS idx_payments_method_status ON payments(payment_method, payment_status_id);
CREATE INDEX IF NOT EXISTS idx_flights_airline_date ON flights(airline_id, departure_datetime);
CREATE INDEX IF NOT EXISTS idx_booking_passengers_booking ON booking_passengers(booking_id);
CREATE INDEX IF NOT EXISTS idx_airlines_active ON airlines(is_active);
CREATE INDEX IF NOT EXISTS idx_bookings_total ON bookings(total_amount);
CREATE INDEX IF NOT EXISTS idx_payments_amount_date ON payments(amount, paid_at);