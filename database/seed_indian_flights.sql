USE airline_reservation;

-- Insert Indian Airlines (ignore duplicates)
INSERT IGNORE INTO airlines (airline_name, airline_code, country, founded_year) VALUES
('Air India', 'AI', 'India', 1932),
('IndiGo', '6E', 'India', 2006),
('Vistara', 'UK', 'India', 2015),
('SpiceJet', 'SG', 'India', 2005),
('GoAir', 'G8', 'India', 2005),
('AirAsia India', 'I5', 'India', 2014);

-- Insert Indian Airports (ignore duplicates)
INSERT IGNORE INTO airports (airport_name, airport_code, city, country) VALUES
('Indira Gandhi International Airport', 'DEL', 'Delhi', 'India'),
('Chhatrapati Shivaji Maharaj International Airport', 'BOM', 'Mumbai', 'India'),
('Kempegowda International Airport', 'BLR', 'Bangalore', 'India'),
('Rajiv Gandhi International Airport', 'HYD', 'Hyderabad', 'India'),
('Netaji Subhas Chandra Bose International Airport', 'CCU', 'Kolkata', 'India'),
('Chennai International Airport', 'MAA', 'Chennai', 'India'),
('Sardar Vallabhbhai Patel International Airport', 'AMD', 'Ahmedabad', 'India'),
('Cochin International Airport', 'COK', 'Kochi', 'India'),
('Pune Airport', 'PNQ', 'Pune', 'India'),
('Goa International Airport', 'GOI', 'Goa', 'India'),
('Jaipur International Airport', 'JAI', 'Jaipur', 'India'),
('Trivandrum International Airport', 'TRV', 'Thiruvananthapuram', 'India'),
('Lal Bahadur Shastri International Airport', 'VNS', 'Varanasi', 'India'),
('Bagdogra Airport', 'IXB', 'Bagdogra', 'India'),
('Sri Guru Ram Das Ji International Airport', 'ATQ', 'Amritsar', 'India');

-- Insert Aircraft (ignore duplicates)
INSERT IGNORE INTO aircraft (aircraft_model, aircraft_type, manufacturer, seating_capacity) VALUES
('Airbus A320neo', 'Narrow-body', 'Airbus', 180),
('Airbus A321neo', 'Narrow-body', 'Airbus', 220),
('Boeing 737-800', 'Narrow-body', 'Boeing', 189),
('Boeing 737 MAX 8', 'Narrow-body', 'Boeing', 178),
('Airbus A350-900', 'Wide-body', 'Airbus', 293),
('Boeing 787-9 Dreamliner', 'Wide-body', 'Boeing', 296);

-- Insert 51 Flights (ignore duplicates to allow adding new flights)
INSERT IGNORE INTO flights (flight_number, airline_id, aircraft_id, origin_airport_id, destination_airport_id, departure_datetime, arrival_datetime, economy_price, business_price, seats_economy, seats_business, status) VALUES
-- Air India Flights (airline_id = 1)
('AI101', 1, 3, 1, 2, '2026-07-15 06:30:00', '2026-07-15 08:45:00', 4500.00, 12000.00, 150, 12, 'Scheduled'),
('AI202', 1, 4, 2, 1, '2026-07-15 09:15:00', '2026-07-15 11:30:00', 4500.00, 12000.00, 150, 12, 'Scheduled'),
('AI303', 1, 6, 1, 3, '2026-07-15 10:00:00', '2026-07-15 12:30:00', 5200.00, 14500.00, 250, 20, 'Scheduled'),
('AI404', 1, 5, 3, 1, '2026-07-15 13:15:00', '2026-07-15 15:45:00', 5200.00, 14500.00, 250, 20, 'Boarding'),
('AI505', 1, 3, 1, 4, '2026-07-15 14:30:00', '2026-07-15 16:15:00', 4800.00, 13000.00, 150, 12, 'Scheduled'),
('AI606', 1, 4, 4, 1, '2026-07-15 17:00:00', '2026-07-15 18:45:00', 4800.00, 13000.00, 150, 12, 'Delayed'),

-- IndiGo Flights (airline_id = 2)
('6E101', 2, 1, 1, 2, '2026-07-15 07:00:00', '2026-07-15 09:15:00', 4200.00, 11500.00, 160, 10, 'Scheduled'),
('6E202', 2, 2, 2, 5, '2026-07-15 10:30:00', '2026-07-15 13:00:00', 5500.00, 15000.00, 180, 15, 'Scheduled'),
('6E303', 2, 1, 5, 6, '2026-07-15 11:45:00', '2026-07-15 14:15:00', 5800.00, 16000.00, 160, 10, 'Scheduled'),
('6E404', 2, 3, 6, 1, '2026-07-15 15:00:00', '2026-07-15 17:20:00', 5200.00, 14500.00, 170, 12, 'Scheduled'),
('6E505', 2, 1, 3, 4, '2026-07-15 16:30:00', '2026-07-15 18:00:00', 3800.00, 10500.00, 160, 10, 'Scheduled'),
('6E606', 2, 2, 4, 7, '2026-07-15 19:00:00', '2026-07-15 21:30:00', 6000.00, 16500.00, 180, 15, 'Scheduled'),

-- Vistara Flights (airline_id = 3)
('UK101', 3, 5, 1, 2, '2026-07-15 08:15:00', '2026-07-15 10:30:00', 5500.00, 17000.00, 250, 20, 'Scheduled'),
('UK202', 3, 6, 2, 8, '2026-07-15 11:00:00', '2026-07-15 13:30:00', 6500.00, 19000.00, 270, 22, 'Scheduled'),
('UK303', 3, 5, 8, 1, '2026-07-15 14:00:00', '2026-07-15 16:15:00', 6500.00, 19000.00, 250, 20, 'Scheduled'),
('UK404', 3, 6, 1, 6, '2026-07-15 17:30:00', '2026-07-15 20:00:00', 5800.00, 17500.00, 270, 22, 'Scheduled'),
('UK505', 3, 5, 3, 1, '2026-07-16 06:45:00', '2026-07-16 09:00:00', 5200.00, 15500.00, 250, 20, 'Scheduled'),
('UK606', 3, 6, 4, 2, '2026-07-16 10:15:00', '2026-07-16 12:45:00', 4800.00, 14000.00, 270, 22, 'Scheduled'),

-- SpiceJet Flights (airline_id = 4)
('SG101', 4, 1, 1, 9, '2026-07-15 07:30:00', '2026-07-15 09:00:00', 3500.00, 9500.00, 160, 10, 'Scheduled'),
('SG202', 4, 2, 9, 1, '2026-07-15 10:00:00', '2026-07-15 11:30:00', 3500.00, 9500.00, 180, 15, 'Scheduled'),
('SG303', 4, 1, 2, 10, '2026-07-15 12:45:00', '2026-07-15 14:15:00', 3200.00, 8500.00, 160, 10, 'Scheduled'),
('SG404', 4, 3, 10, 2, '2026-07-15 15:30:00', '2026-07-15 17:00:00', 3200.00, 8500.00, 170, 12, 'Scheduled'),
('SG505', 4, 1, 3, 11, '2026-07-15 18:00:00', '2026-07-15 19:30:00', 2800.00, 7500.00, 160, 10, 'Scheduled'),
('SG606', 4, 2, 11, 3, '2026-07-16 07:00:00', '2026-07-16 08:30:00', 2800.00, 7500.00, 180, 15, 'Scheduled'),

-- GoAir Flights (airline_id = 5)
('G8101', 5, 1, 1, 2, '2026-07-15 08:00:00', '2026-07-15 10:15:00', 4000.00, 10800.00, 160, 10, 'Scheduled'),
('G8202', 5, 2, 2, 12, '2026-07-15 11:30:00', '2026-07-15 13:45:00', 4800.00, 13000.00, 180, 15, 'Scheduled'),
('G8303', 5, 1, 12, 1, '2026-07-15 14:30:00', '2026-07-15 16:45:00', 4800.00, 13000.00, 160, 10, 'Scheduled'),
('G8404', 5, 3, 1, 13, '2026-07-15 17:00:00', '2026-07-15 18:30:00', 3500.00, 9500.00, 170, 12, 'Scheduled'),
('G8505', 5, 1, 13, 1, '2026-07-16 08:30:00', '2026-07-16 10:00:00', 3500.00, 9500.00, 160, 10, 'Scheduled'),

-- AirAsia India Flights (airline_id = 6)
('I5101', 6, 1, 1, 14, '2026-07-15 09:00:00', '2026-07-15 10:30:00', 3000.00, 8000.00, 160, 10, 'Scheduled'),
('I5202', 6, 2, 14, 15, '2026-07-15 11:00:00', '2026-07-15 12:30:00', 3200.00, 8800.00, 180, 15, 'Scheduled'),
('I5303', 6, 1, 15, 1, '2026-07-15 13:45:00', '2026-07-15 15:15:00', 3200.00, 8800.00, 160, 10, 'Scheduled'),
('I5404', 6, 3, 2, 3, '2026-07-15 16:00:00', '2026-07-15 18:30:00', 4200.00, 11200.00, 170, 12, 'Scheduled'),
('I5505', 6, 1, 4, 5, '2026-07-15 19:30:00', '2026-07-15 21:45:00', 5600.00, 15000.00, 160, 10, 'Scheduled'),

-- Additional connecting andreturn flights
('AI707', 1, 5, 5, 7, '2026-07-16 07:00:00', '2026-07-16 09:45:00', 4900.00, 13500.00, 250, 20, 'Scheduled'),
('AI808', 1, 6, 7, 5, '2026-07-16 10:30:00', '2026-07-16 13:15:00', 4900.00, 13500.00, 270, 22, 'Scheduled'),
('6E707', 2, 1, 6, 8, '2026-07-16 08:00:00', '2026-07-16 10:30:00', 6200.00, 16800.00, 160, 10, 'Scheduled'),
('6E808', 2, 2, 8, 6, '2026-07-16 11:45:00', '2026-07-16 14:15:00', 6200.00, 16800.00, 180, 15, 'Scheduled'),
('UK707', 3, 5, 9, 3, '2026-07-16 09:15:00', '2026-07-16 11:00:00', 3400.00, 9800.00, 250, 20, 'Scheduled'),
('UK808', 3, 6, 3, 9, '2026-07-16 12:30:00', '2026-07-16 14:15:00', 3400.00, 9800.00, 270, 22, 'Scheduled'),
('SG707', 4, 1, 10, 11, '2026-07-16 07:30:00', '2026-07-16 09:00:00', 2600.00, 7000.00, 160, 10, 'Scheduled'),
('SG808', 4, 2, 11, 10, '2026-07-16 10:15:00', '2026-07-16 11:45:00', 2600.00, 7000.00, 180, 15, 'Cancelled'),
('G8707', 5, 3, 13, 6, '2026-07-16 08:00:00', '2026-07-16 10:15:00', 4100.00, 11200.00, 170, 12, 'Scheduled'),
('G8808', 5, 1, 6, 13, '2026-07-16 11:30:00', '2026-07-16 13:45:00', 4100.00, 11200.00, 160, 10, 'Scheduled'),
('I5707', 6, 2, 14, 4, '2026-07-16 09:00:00', '2026-07-16 11:00:00', 3800.00, 10200.00, 180, 15, 'Scheduled'),
('I5808', 6, 1, 4, 14, '2026-07-16 12:15:00', '2026-07-16 14:15:00', 3800.00, 10200.00, 160, 10, 'Scheduled'),
('AI901', 1, 5, 5, 12, '2026-07-17 08:00:00', '2026-07-17 10:45:00', 4200.00, 12000.00, 250, 20, 'Scheduled'),
('AI902', 1, 3, 12, 5, '2026-07-17 11:30:00', '2026-07-17 14:15:00', 4200.00, 12000.00, 150, 12, 'Scheduled'),
('6E901', 2, 1, 13, 1, '2026-07-17 07:00:00', '2026-07-17 08:45:00', 3600.00, 10000.00, 160, 10, 'Scheduled'),
('6E902', 2, 2, 14, 2, '2026-07-17 09:30:00', '2026-07-17 11:45:00', 4500.00, 12000.00, 180, 15, 'Scheduled'),
('UK901', 3, 6, 15, 3, '2026-07-17 10:00:00', '2026-07-17 12:30:00', 5800.00, 17000.00, 270, 22, 'Scheduled');

-- Mark some flights as Delayed for variety
UPDATE flights SET status = 'Delayed' WHERE flight_number IN ('AI606', 'UK808', 'UK901');

-- Mark some flights as Cancelled
UPDATE flights SET status = 'Cancelled' WHERE flight_number IN ('SG808', 'AI902');
