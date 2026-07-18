-- Day 4 SQL Reporting Queries

-- 1. Total Revenue by Payment Method
SELECT 
    payment_method,
    COUNT(*) AS transaction_count,
    COALESCE(SUM(amount), 0) AS total_revenue,
    COALESCE(AVG(amount), 0) AS avg_transaction_amount
FROM payments
WHERE payment_status_id = 2  -- Completed
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- 2. Daily Revenue Report (Last 30 days)
SELECT 
    DATE(paid_at) AS payment_date,
    COUNT(*) AS transaction_count,
    COALESCE(SUM(amount), 0) AS daily_revenue
FROM payments
WHERE payment_status_id = 2
    AND paid_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(paid_at)
ORDER BY payment_date DESC;

-- 3. Booking Statistics by Flight
SELECT 
    f.flight_number,
    a.airline_name,
    COUNT(b.id) AS total_bookings,
    COALESCE(SUM(b.total_amount), 0) AS total_revenue,
    COUNT(DISTINCT bp.passenger_id) AS total_passengers
FROM bookings b
INNER JOIN flights f ON b.flight_id = f.id
INNER JOIN airlines a ON f.airline_id = a.id
LEFT JOIN booking_passengers bp ON b.id = bp.booking_id
GROUP BY f.id, f.flight_number, a.airline_name
ORDER BY total_bookings DESC;

-- 4. Payment Status Distribution with CASE
SELECT 
    CASE 
        WHEN ps.status_name = 'Completed' THEN 'Completed'
        WHEN ps.status_name = 'Pending' THEN 'Pending'
        WHEN ps.status_name = 'Failed' THEN 'Failed'
        WHEN ps.status_name = 'Refunded' THEN 'Refunded'
        ELSE 'Other'
    END AS status_category,
    COUNT(*) AS count,
    COALESCE(SUM(p.amount), 0) AS total_amount,
    COALESCE(AVG(p.amount), 0) AS avg_amount
FROM payments p
INNER JOIN payment_status ps ON p.payment_status_id = ps.id
GROUP BY status_category
ORDER BY count DESC;

-- 5. Stored Procedure: Get Total Revenue
DELIMITER //

CREATE PROCEDURE IF NOT EXISTS GetTotalRevenue()
BEGIN
    SELECT 
        COUNT(*) AS total_transactions,
        COALESCE(SUM(amount), 0) AS total_revenue,
        COALESCE(AVG(amount), 0) AS average_payment,
        MIN(paid_at) AS first_payment_date,
        MAX(paid_at) AS last_payment_date
    FROM payments
    WHERE payment_status_id = 2;
END //

DELIMITER ;

-- 6. Stored Procedure: Get Revenue by Airline
DELIMITER //

CREATE PROCEDURE IF NOT EXISTS GetRevenueByAirline(IN start_date DATE, IN end_date DATE)
BEGIN
    SELECT 
        a.airline_name,
        a.airline_code,
        COUNT(DISTINCT p.id) AS total_bookings,
        COALESCE(SUM(p.amount), 0) AS total_revenue,
        COALESCE(AVG(p.amount), 0) AS avg_booking_value
    FROM payments p
    INNER JOIN bookings b ON p.booking_id = b.id
    INNER JOIN flights f ON b.flight_id = f.id
    INNER JOIN airlines a ON f.airline_id = a.id
    WHERE p.payment_status_id = 2
        AND DATE(p.paid_at) BETWEEN start_date AND end_date
    GROUP BY a.id, a.airline_name, a.airline_code
    ORDER BY total_revenue DESC;
END //

DELIMITER ;

-- 7. Stored Procedure: Get Booking Statistics
DELIMITER //

CREATE PROCEDURE IF NOT EXISTS GetBookingStatistics(IN start_date DATE, IN end_date DATE)
BEGIN
    SELECT 
        DATE(b.booked_at) AS booking_date,
        COUNT(*) AS bookings_count,
        COUNT(DISTINCT b.user_id) AS unique_customers,
        COALESCE(SUM(b.total_amount), 0) AS daily_revenue,
        AVG(b.total_amount) AS avg_booking_value
    FROM bookings b
    WHERE DATE(b.booked_at) BETWEEN start_date AND end_date
    GROUP BY DATE(b.booked_at)
    ORDER BY booking_date DESC;
END //

DELIMITER ;

-- 8. Index for performance optimization
CREATE INDEX IF NOT EXISTS idx_payments_status_date ON payments(payment_status_id, paid_at);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(booked_at);
CREATE INDEX IF NOT EXISTS idx_flights_route ON flights(origin_airport_id, destination_airport_id);

-- 9. Revenue by Route (Origin -> Destination)
SELECT 
    o.city AS origin_city,
    d.city AS destination_city,
    a.airline_name,
    COUNT(b.id) AS booking_count,
    COALESCE(SUM(p.amount), 0) AS total_revenue
FROM bookings b
INNER JOIN flights f ON b.flight_id = f.id
INNER JOIN airports o ON f.origin_airport_id = o.id
INNER JOIN airports d ON f.destination_airport_id = d.id
INNER JOIN airlines a ON f.airline_id = a.id
INNER JOIN payments p ON b.id = p.booking_id
WHERE p.payment_status_id = 2
GROUP BY o.id, d.id, a.id
ORDER BY total_revenue DESC
LIMIT 20;

-- 10. Peak Booking Hours Analysis
SELECT 
    HOUR(b.booked_at) AS booking_hour,
    COUNT(*) AS booking_count,
    COALESCE(SUM(b.total_amount), 0) AS revenue
FROM bookings b
GROUP BY HOUR(b.booked_at)
ORDER BY booking_count DESC;