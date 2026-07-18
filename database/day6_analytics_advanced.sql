-- ============================================================
-- DAY 6: BUSINESS ANALYTICS & ADVANCED SQL
-- ============================================================

-- ============================================================
-- VIEWS
-- ============================================================

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
    CONCAT(ap1.airport_code, ' → ', ap2.airport_code) AS route_name,
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

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_bookings_status_date ON bookings(booking_status_id, booked_at);
CREATE INDEX IF NOT EXISTS idx_payments_date_status ON payments(paid_at, payment_status_id);
CREATE INDEX IF NOT EXISTS idx_flights_datetime ON flights(departure_datetime, status);
CREATE INDEX IF NOT EXISTS idx_bookings_flight ON bookings(flight_id);
CREATE INDEX IF NOT EXISTS idx_payments_amount ON payments(amount);
CREATE INDEX IF NOT EXISTS idx_bookings_amount ON bookings(total_amount);

-- ============================================================
-- STORED PROCEDURES
-- ============================================================

DELIMITER //

-- Revenue Report Procedure
CREATE PROCEDURE sp_generate_revenue_report(
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        DATE(p.paid_at) AS date,
        COUNT(DISTINCT b.id) AS bookings,
        SUM(p.amount) AS revenue,
        AVG(p.amount) AS avg_transaction,
        COUNT(DISTINCT b.user_id) AS unique_customers
    FROM payments p
    JOIN bookings b ON p.booking_id = b.id
    WHERE DATE(p.paid_at) BETWEEN p_start_date AND p_end_date
    AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
    GROUP BY DATE(p.paid_at)
    ORDER BY date DESC;
END //

-- Booking Report Procedure
CREATE PROCEDURE sp_generate_booking_report(
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        DATE(b.booked_at) AS date,
        bs.status_name,
        COUNT(b.id) AS booking_count,
        SUM(b.total_amount) AS total_value,
        COUNT(DISTINCT b.user_id) AS unique_users
    FROM bookings b
    JOIN booking_status bs ON b.booking_status_id = bs.id
    WHERE DATE(b.booked_at) BETWEEN p_start_date AND p_end_date
    GROUP BY DATE(b.booked_at), bs.status_name
    ORDER BY date DESC, booking_count DESC;
END //

-- Customer Report Procedure
CREATE PROCEDURE sp_generate_customer_report(
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        u.id,
        u.full_name,
        u.email,
        u.created_at AS registration_date,
        COUNT(DISTINCT b.id) AS total_bookings,
        COALESCE(SUM(p.amount), 0) AS total_spent,
        COALESCE(AVG(p.amount), 0) AS avg_booking_value,
        MAX(b.booked_at) AS last_booking_date
    FROM users u
    LEFT JOIN bookings b ON u.id = b.user_id 
        AND DATE(b.booked_at) BETWEEN p_start_date AND p_end_date
    LEFT JOIN payments p ON b.id = p.booking_id 
        AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
    GROUP BY u.id, u.full_name, u.email, u.created_at
    ORDER BY total_spent DESC;
END //

-- Route Report Procedure
CREATE PROCEDURE sp_generate_route_report()
BEGIN
    SELECT 
        CONCAT(ap1.airport_code, ' → ', ap2.airport_code) AS route,
        a.airline_name,
        COUNT(DISTINCT f.id) AS flight_count,
        COUNT(DISTINCT b.id) AS booking_count,
        COALESCE(SUM(p.amount), 0) AS total_revenue,
        ROUND((COUNT(bp.id) / (f.seats_economy + f.seats_business)) * 100, 2) AS occupancy_rate
    FROM flights f
    JOIN airlines a ON f.airline_id = a.id
    JOIN airports ap1 ON f.origin_airport_id = ap1.id
    JOIN airports ap2 ON f.destination_airport_id = ap2.id
    LEFT JOIN bookings b ON f.id = b.flight_id
    LEFT JOIN payments p ON b.id = p.booking_id 
        AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
    LEFT JOIN booking_passengers bp ON b.id = bp.booking_id
    GROUP BY ap1.airport_code, ap2.airport_code, a.airline_name, f.seats_economy, f.seats_business
    ORDER BY total_revenue DESC;
END //

-- Flight Report Procedure
CREATE PROCEDURE sp_generate_flight_report(
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        f.flight_number,
        a.airline_name,
        f.departure_datetime,
        f.arrival_datetime,
        f.status,
        f.seats_economy + f.seats_business AS total_seats,
        COUNT(DISTINCT b.id) AS bookings,
        COALESCE(SUM(p.amount), 0) AS revenue,
        ROUND((COUNT(bp.id) / (f.seats_economy + f.seats_business)) * 100, 2) AS occupancy_rate
    FROM flights f
    JOIN airlines a ON f.airline_id = a.id
    LEFT JOIN bookings b ON f.id = b.flight_id
        AND DATE(b.booked_at) BETWEEN p_start_date AND p_end_date
    LEFT JOIN payments p ON b.id = p.booking_id 
        AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
    LEFT JOIN booking_passengers bp ON b.id = bp.booking_id
    GROUP BY f.id, f.flight_number, a.airline_name, f.departure_datetime, 
             f.arrival_datetime, f.status, f.seats_economy, f.seats_business
    ORDER BY revenue DESC;
END //

-- Occupancy Report Procedure
CREATE PROCEDURE sp_generate_occupancy_report()
BEGIN
    SELECT 
        a.airline_name,
        COUNT(f.id) AS total_flights,
        SUM(f.seats_economy + f.seats_business) AS total_capacity,
        COUNT(bp.id) AS seats_sold,
        ROUND((COUNT(bp.id) / SUM(f.seats_economy + f.seats_business)) * 100, 2) AS occupancy_rate
    FROM airlines a
    JOIN flights f ON a.id = f.airline_id
    LEFT JOIN bookings b ON f.id = b.flight_id
    LEFT JOIN booking_passengers bp ON b.id = bp.booking_id
    GROUP BY a.id, a.airline_name
    ORDER BY occupancy_rate DESC;
END //

DELIMITER ;

-- ============================================================
-- TRIGGERS
-- ============================================================

DELIMITER //

-- Audit Log Trigger for Bookings
CREATE TRIGGER trg_booking_audit
AFTER INSERT ON bookings
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
    VALUES (
        NEW.user_id,
        'BOOKING_CREATED',
        'booking',
        NEW.id,
        CONCAT('Booking created with reference: ', NEW.booking_reference, ' for user ID: ', NEW.user_id),
        NOW()
    );
END //

-- Audit Log Trigger for Booking Updates
CREATE TRIGGER trg_booking_update_audit
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
    VALUES (
        NEW.user_id,
        'BOOKING_UPDATED',
        'booking',
        NEW.id,
        CONCAT('Booking status changed from: ', OLD.booking_status_id, ' to: ', NEW.booking_status_id),
        NOW()
    );
END //

-- Audit Log Trigger for Payments
CREATE TRIGGER trg_payment_audit
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    DECLARE user_id_val INT;
    
    SELECT b.user_id INTO user_id_val 
    FROM bookings b 
    WHERE b.id = NEW.booking_id;
    
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
    VALUES (
        user_id_val,
        'PAYMENT_CREATED',
        'payment',
        NEW.id,
        CONCAT('Payment of ', NEW.amount, ' via ', NEW.payment_method, ' with reference: ', NEW.payment_reference),
        NOW()
    );
END //

-- Log booking history
CREATE TRIGGER trg_booking_history
AFTER INSERT ON booking_passengers
FOR EACH ROW
BEGIN
    DECLARE booking_ref VARCHAR(30);
    
    SELECT b.booking_reference INTO booking_ref 
    FROM bookings b 
    WHERE b.id = NEW.booking_id;
    
    INSERT INTO audit_logs (action, entity_type, entity_id, details, created_at)
    VALUES (
        'PASSENGER_ADDED',
        'booking_passenger',
        NEW.id,
        CONCAT('Passenger added to booking: ', booking_ref),
        NOW()
    );
END //

DELIMITER ;

-- ============================================================
-- INDEXES FOR QUERY OPTIMIZATION
-- ============================================================

-- Comprehensive indexes for analytics queries
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

-- ============================================================
-- ADVANCED SQL: WINDOW FUNCTIONS IN QUERIES
-- ============================================================

-- Top Customers with Ranking
-- This query uses ROW_NUMBER(), RANK(), and DENSE_RANK()
-- Run this to get top customers
-- SELECT 
--     user_id,
--     full_name,
--     email,
--     total_bookings,
--     total_spent,
--     ROW_NUMBER() OVER (ORDER BY total_spent DESC) AS row_num,
--     RANK() OVER (ORDER BY total_spent DESC) AS rank_val,
--     DENSE_RANK() OVER (ORDER BY total_spent DESC) AS dense_rank_val,
--     LAG(total_spent, 1) OVER (ORDER BY total_spent DESC) AS prev_customer_spend,
--     LEAD(total_spent, 1) OVER (ORDER BY total_spent DESC) AS next_customer_spend,
--     (total_spent - LAG(total_spent, 1) OVER (ORDER BY total_spent DESC)) AS spend_difference
-- FROM vw_customer_summary
-- WHERE total_bookings > 0
-- ORDER BY total_spent DESC
-- LIMIT 10;

-- Monthly Revenue Comparison with Previous Month
-- SELECT 
--     month,
--     revenue,
--     LAG(revenue, 1) OVER (ORDER BY month) AS previous_month_revenue,
--     revenue - LAG(revenue, 1) OVER (ORDER BY month) AS revenue_growth,
--     ROUND(((revenue - LAG(revenue, 1) OVER (ORDER BY month)) / 
--            NULLIF(LAG(revenue, 1) OVER (ORDER BY month), 0)) * 100, 2) AS growth_percentage
-- FROM (
--     SELECT 
--         DATE_FORMAT(paid_at, '%Y-%m') AS month,
--         SUM(amount) AS revenue
--     FROM payments
--     WHERE payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
--     GROUP BY DATE_FORMAT(paid_at, '%Y-%m')
-- ) monthly_data;

-- ============================================================
-- COMMON TABLE EXPRESSIONS (CTEs)
-- ============================================================

-- Revenue Analysis CTE
-- WITH RevenueAnalysis AS (
--     SELECT 
--         a.airline_name,
--         DATE_FORMAT(p.paid_at, '%Y-%m') AS month,
--         SUM(p.amount) AS revenue,
--         COUNT(DISTINCT b.id) AS bookings
--     FROM payments p
--     JOIN bookings b ON p.booking_id = b.id
--     JOIN flights f ON b.flight_id = f.id
--     JOIN airlines a ON f.airline_id = a.id
--     WHERE p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
--     GROUP BY a.airline_name, DATE_FORMAT(p.paid_at, '%Y-%m')
-- )
-- SELECT * FROM RevenueAnalysis ORDER BY month DESC, revenue DESC;

-- Route Ranking CTE
-- WITH RouteRanking AS (
--     SELECT 
--         CONCAT(ap1.airport_code, ' → ', ap2.airport_code) AS route,
--         COUNT(DISTINCT b.id) AS bookings,
--         COALESCE(SUM(p.amount), 0) AS revenue,
--         ROUND((COUNT(bp.id) / (f.seats_economy + f.seats_business)) * 100, 2) AS occupancy_rate,
--         RANK() OVER (PARTITION BY ap1.airport_code ORDER BY COUNT(DISTINCT b.id) DESC) AS route_rank
--     FROM flights f
--     JOIN airports ap1 ON f.origin_airport_id = ap1.id
--     JOIN airports ap2 ON f.destination_airport_id = ap2.id
--     LEFT JOIN bookings b ON f.id = b.flight_id
--     LEFT JOIN payments p ON b.id = p.booking_id 
--         AND p.payment_status_id = (SELECT id FROM payment_status WHERE status_name = 'Paid' LIMIT 1)
--     LEFT JOIN booking_passengers bp ON b.id = bp.booking_id
--     GROUP BY ap1.airport_code, ap2.airport_code, f.seats_economy, f.seats_business
-- )
-- SELECT * FROM RouteRanking WHERE route_rank <= 5;

-- ============================================================
-- POWER BI DATASET PREPARATION
-- ============================================================

-- FactBookings table for Power BI
-- CREATE TABLE IF NOT EXISTS fact_bookings (
--     booking_id INT,
--     booking_reference VARCHAR(30),
--     booking_date DATE,
--     booking_status VARCHAR(50),
--     flight_id INT,
--     flight_number VARCHAR(20),
--     airline_id INT,
--     airline_name VARCHAR(150),
--     customer_id INT,
--     customer_name VARCHAR(150),
--     customer_email VARCHAR(150),
--     origin_airport VARCHAR(10),
--     origin_city VARCHAR(100),
--     destination_airport VARCHAR(10),
--     destination_city VARCHAR(100),
--     aircraft_model VARCHAR(100),
--     total_amount DECIMAL(10,2),
--     paid_amount DECIMAL(10,2),
--     passenger_count INT,
--     payment_method VARCHAR(30),
--     payment_status VARCHAR(50),
--     created_at TIMESTAMP
-- );

-- FactPayments table for Power BI
-- CREATE TABLE IF NOT EXISTS fact_payments (
--     payment_id INT,
--     payment_reference VARCHAR(30),
--     booking_id INT,
--     booking_reference VARCHAR(30),
--     payment_date DATE,
--     payment_method VARCHAR(30),
--     payment_status VARCHAR(50),
--     amount DECIMAL(10,2),
--     airline_id INT,
--     airline_name VARCHAR(150),
--     customer_id INT,
--     customer_name VARCHAR(150),
--     created_at TIMESTAMP
-- );

-- DimCustomer table for Power BI
-- CREATE TABLE IF NOT EXISTS dim_customer (
--     customer_id INT,
--     customer_name VARCHAR(150),
--     email VARCHAR(150),
--     mobile VARCHAR(20),
--     registration_date DATE,
--     total_bookings INT,
--     total_spent DECIMAL(10,2),
--     avg_booking_value DECIMAL(10,2),
--     last_booking_date DATE,
--     created_at TIMESTAMP
-- );

-- DimFlight table for Power BI
-- CREATE TABLE IF NOT EXISTS dim_flight (
--     flight_id INT,
--     flight_number VARCHAR(20),
--     airline_id INT,
--     airline_name VARCHAR(150),
--     aircraft_model VARCHAR(100),
--     origin_airport VARCHAR(10),
--     origin_city VARCHAR(100),
--     destination_airport VARCHAR(10),
--     destination_city VARCHAR(100),
--     departure_datetime DATETIME,
--     arrival_datetime DATETIME,
--     total_seats INT,
--     status VARCHAR(20),
--     created_at TIMESTAMP
-- );

-- DimAirline table for Power BI
-- CREATE TABLE IF NOT EXISTS dim_airline (
--     airline_id INT,
--     airline_name VARCHAR(150),
--     airline_code VARCHAR(10),
--     country VARCHAR(100),
--     founded_year INT,
--     total_flights INT,
--     total_bookings INT,
--     total_revenue DECIMAL(10,2),
--     avg_ticket_price DECIMAL(10,2),
--     created_at TIMESTAMP
-- );

-- DimRoute table for Power BI
-- CREATE TABLE IF NOT EXISTS dim_route (
--     route_id INT,
--     route_name VARCHAR(30),
--     origin_airport VARCHAR(10),
--     origin_city VARCHAR(100),
--     destination_airport VARCHAR(10),
--     destination_city VARCHAR(100),
--     airline_id INT,
--     airline_name VARCHAR(150),
--     total_flights INT,
--     total_bookings INT,
--     total_revenue DECIMAL(10,2),
--     occupancy_rate DECIMAL(5,2),
--     created_at TIMESTAMP
-- );

-- DimDate table for Power BI
-- CREATE TABLE IF NOT EXISTS dim_date (
--     date_id INT PRIMARY KEY AUTO_INCREMENT,
--     date DATE,
--     day INT,
--     month INT,
--     month_name VARCHAR(20),
--     quarter INT,
--     year INT,
--     day_of_week INT,
--     day_name VARCHAR(20),
--     is_weekend TINYINT(1),
--     is_holiday TINYINT(1) DEFAULT 0
-- );