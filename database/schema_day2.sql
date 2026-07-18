-- Day 2 Complete Schema Updates
-- Run this to update existing database for Flight Management & Search modules

USE airline_reservation;

-- Update airlines table to match requirements
ALTER TABLE airlines 
    ADD COLUMN status VARCHAR(20) DEFAULT 'Active' AFTER country,
    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER status;

-- Update existing records
UPDATE airlines SET status = 'Active' WHERE status IS NULL;

-- Create routes table (Module 2)
CREATE TABLE IF NOT EXISTS routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    source_airport VARCHAR(100) NOT NULL,
    destination_airport VARCHAR(100) NOT NULL,
    distance_km DECIMAL(10,2) NOT NULL,
    duration_minutes INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_route_different CHECK (source_airport != destination_airport),
    CONSTRAINT chk_distance_positive CHECK (distance_km > 0),
    CONSTRAINT chk_duration_positive CHECK (duration_minutes > 0)
) ENGINE=InnoDB;

-- Update flights table structure (Module 3)
-- Note: Based on existing schema, we'll work with current structure
-- Adding available_seats tracking
ALTER TABLE flights 
    ADD COLUMN available_seats INT DEFAULT 0 AFTER business_price;

-- Set available_seats based on aircraft capacity
UPDATE flights f 
JOIN aircraft a ON f.aircraft_id = a.id 
SET f.available_seats = a.seating_capacity;

-- Create flight_schedule table (Module 4)
CREATE TABLE IF NOT EXISTS flight_schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    flight_id INT NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    terminal VARCHAR(10) DEFAULT NULL,
    gate_number VARCHAR(10) DEFAULT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_schedule_flight FOREIGN KEY (flight_id) REFERENCES flights(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_arrival_after_departure CHECK (arrival_time > departure_time),
    CONSTRAINT chk_price_positive CHECK (price > 0)
) ENGINE=InnoDB;

-- Indexes for performance
CREATE INDEX idx_airlines_code ON airlines(airline_code);
CREATE INDEX idx_airlines_status ON airlines(status);
CREATE INDEX idx_routes_source ON routes(source_airport);
CREATE INDEX idx_routes_destination ON routes(destination_airport);
CREATE INDEX idx_flights_status ON flights(status);
CREATE INDEX idx_flights_datetime ON flights(departure_datetime);
CREATE INDEX idx_schedule_flight ON flight_schedule(flight_id);
CREATE INDEX idx_schedule_departure ON flight_schedule(departure_time);