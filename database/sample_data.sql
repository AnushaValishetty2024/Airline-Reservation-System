USE airline_reservation;

INSERT INTO user_roles (role_name, description) VALUES
('Admin', 'System administrator'),
('User', 'Standard system user');

INSERT INTO users (full_name, email, mobile_number, password_hash, role_id) VALUES
('System Administrator', 'admin@airline.com', '+15551234567', 'scrypt:32768:8:1$tocdie5kUXPS2TOA$66079396059abd0f0ae53f2e1ec50546ca7f275bad187f7c1e549f3b8005d8243a0c607b1394c0bcda47ad8e9921101f51542edc2f285e0ffe3d3135310ce661', 1),
('John Doe', 'john.doe@example.com', '+15557654321', 'scrypt:32768:8:1$UCYPpn89hVssM6rK$d4928d9e916eb9020af756275fd4b5f5024b19e3fab9f878effc21d81002906fc324c069468bad2b66a337c97b0eebe14d31616478e8c38ff4351a23c005d2d2', 2);

INSERT INTO airlines (airline_name, airline_code, country, founded_year) VALUES
('Skyline Airways', 'SKY', 'United States', 2005),
('Blue Horizon Air', 'BHA', 'Canada', 1998);

INSERT INTO airports (airport_name, airport_code, city, country) VALUES
('John F. Kennedy International Airport', 'JFK', 'New York', 'United States'),
('Los Angeles International Airport', 'LAX', 'Los Angeles', 'United States'),
('Toronto Pearson International Airport', 'YYZ', 'Toronto', 'Canada');

INSERT INTO aircraft (aircraft_model, aircraft_type, manufacturer, seating_capacity) VALUES
('Boeing 737', 'Narrow-body', 'Boeing', 180),
('Airbus A320', 'Narrow-body', 'Airbus', 180),
('Boeing 777', 'Wide-body', 'Boeing', 320);

INSERT INTO flights (flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id, departure_datetime, arrival_datetime, economy_price, business_price) VALUES
('SKY101', 1, 1, 1, 2, '2026-07-10 08:00:00', '2026-07-10 11:30:00', 220.00, 420.00),
('BHA202', 2, 2, 3, 1, '2026-07-11 09:00:00', '2026-07-11 13:15:00', 180.00, 360.00);

INSERT INTO booking_status (status_name, description) VALUES
('Pending', 'Booking created but not confirmed'),
('Confirmed', 'Booking confirmed'),
('Cancelled', 'Booking cancelled');

INSERT INTO payment_status (status_name, description) VALUES
('Pending', 'Payment pending'),
('Completed', 'Payment completed'),
('Failed', 'Payment failed');

INSERT INTO ticket_status (status_name, description) VALUES
('Booked', 'Ticket booked'),
('Checked In', 'Passenger checked in'),
('Cancelled', 'Ticket cancelled');

INSERT INTO passengers (full_name, email, mobile_number, passport_number) VALUES
('Alice Walker', 'alice@example.com', '+15550000001', 'P1234567'),
('Bob Miller', 'bob@example.com', '+15550000002', 'P7654321');

INSERT INTO bookings (booking_reference, user_id, flight_id, booking_status_id, total_amount) VALUES
('BK1001', 2, 1, 2, 440.00);

INSERT INTO booking_passengers (booking_id, passenger_id, ticket_status_id, seat_number) VALUES
(1, 1, 1, '12A');

INSERT INTO payments (booking_id, payment_reference, amount, payment_method, payment_status_id) VALUES
(1, 'PAY1001', 440.00, 'Card', 2);
