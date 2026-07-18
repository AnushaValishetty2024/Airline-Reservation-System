-- Day 4 Schema Updates

-- Add dynamic pricing columns to flights
ALTER TABLE flights 
ADD COLUMN IF NOT EXISTS current_price DECIMAL(10,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS last_price_update DATETIME DEFAULT NULL;

-- Create holidays table
CREATE TABLE IF NOT EXISTS holidays (
    id INT AUTO_INCREMENT PRIMARY KEY,
    holiday_name VARCHAR(150) NOT NULL,
    holiday_date DATE NOT NULL,
    description VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_holiday_date (holiday_date)
) ENGINE=InnoDB;

-- Create pricing_rules table
CREATE TABLE IF NOT EXISTS pricing_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL UNIQUE,
    multiplier DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    active TINYINT(1) DEFAULT 1,
    description VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Update payments table to include transaction_id and is_read for notifications
ALTER TABLE payments 
ADD COLUMN IF NOT EXISTS transaction_id VARCHAR(100) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'info',
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read, created_at);
CREATE INDEX IF NOT EXISTS idx_holidays_date ON holidays(holiday_date);
CREATE INDEX IF NOT EXISTS idx_payments_booking ON payments(booking_id);

-- Seed initial pricing rules
INSERT INTO pricing_rules (rule_name, multiplier, description) VALUES
('weekend_pricing', 1.15, '15% increase on weekends (Saturday and Sunday)'),
('holiday_pricing', 1.20, '20% increase on holidays'),
('low_seat_pricing', 1.25, '25% increase when less than 20% seats available')
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- Seed some Indian holidays for testing
INSERT INTO holidays (holiday_name, holiday_date, description) VALUES
('Republic Day', '2026-01-26', 'Indian Republic Day'),
('Holi', '2026-03-17', 'Festival of Colors'),
('Independence Day', '2026-08-15', 'Indian Independence Day'),
('Diwali', '2026-11-01', 'Festival of Lights'),
('Christmas', '2026-12-25', 'Christmas Day')
ON DUPLICATE KEY UPDATE description=VALUES(description);