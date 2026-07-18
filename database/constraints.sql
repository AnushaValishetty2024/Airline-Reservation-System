USE airline_reservation;

ALTER TABLE users
    ADD CONSTRAINT chk_users_email_format CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'),
    ADD CONSTRAINT chk_users_mobile CHECK (mobile_number REGEXP '^[0-9+().-]{7,15}$');

ALTER TABLE airlines
    ADD CONSTRAINT chk_airlines_code CHECK (char_length(airline_code) BETWEEN 2 AND 10),
    ADD CONSTRAINT chk_airlines_year CHECK (founded_year IS NULL OR founded_year BETWEEN 1900 AND 2100);

ALTER TABLE airports
    ADD CONSTRAINT chk_airports_code CHECK (char_length(airport_code) BETWEEN 3 AND 5);

ALTER TABLE aircraft
    ADD CONSTRAINT chk_aircraft_capacity CHECK (seating_capacity > 0);

ALTER TABLE flights
    ADD CONSTRAINT chk_flights_prices CHECK (economy_price > 0 AND business_price > 0),
    ADD CONSTRAINT chk_flights_seats CHECK (seats_economy > 0 AND seats_business > 0),
    ADD CONSTRAINT chk_flights_dates CHECK (arrival_datetime > departure_datetime);

ALTER TABLE bookings
    ADD CONSTRAINT chk_bookings_amount CHECK (total_amount > 0);

ALTER TABLE payments
    ADD CONSTRAINT chk_payments_amount CHECK (amount > 0);
