DROP DATABASE IF EXISTS parking_sys;
CREATE DATABASE parking_sys;
USE parking_sys;

-- ==========================================
-- ADVANCED DBMS SCHEMA FOR REVIEW 3
-- Includes Normalization (3NF), Constraints, Triggers
-- ==========================================

-- 1. Users Table (Authentication)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator'
);

-- 2. Vehicle Types Table (Normalization: 3NF Separation)
-- Prevents update anomalies on pricing and transitive dependencies
CREATE TABLE vehicle_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(20) NOT NULL UNIQUE,
    hourly_rate DECIMAL(5, 2) NOT NULL CHECK (hourly_rate >= 0) -- Constraint
);

-- 3. Parking Zones Table (Location mapping)
CREATE TABLE parking_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

-- 4. Parking Spots Table (Physical slots)
-- Depends on Zone and Type
CREATE TABLE parking_spots (
    spot_id INT AUTO_INCREMENT PRIMARY KEY,
    spot_number VARCHAR(10) NOT NULL UNIQUE,
    zone_id INT NOT NULL,
    type_id INT NOT NULL,
    is_occupied BOOLEAN DEFAULT FALSE,
    vehicle_plate VARCHAR(20) DEFAULT NULL,
    FOREIGN KEY (zone_id) REFERENCES parking_zones(id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES vehicle_types(id) ON DELETE CASCADE
);

-- 5. Monthly Passes Table (Subscriptions)
CREATE TABLE monthly_passes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_plate VARCHAR(20) NOT NULL UNIQUE,
    owner_name VARCHAR(50) NOT NULL,
    valid_until DATE NOT NULL
);

-- 6. Transactions Table (ACID Core structure)
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_plate VARCHAR(20) NOT NULL,
    spot_id INT NOT NULL,
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    exit_time DATETIME DEFAULT NULL,
    fee DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (spot_id) REFERENCES parking_spots(spot_id)
);

-- 7. Payments Table (Separated for 3NF - Financial records)
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    payment_method VARCHAR(20) NOT NULL, -- Cash, Card, UPI, Pass
    amount DECIMAL(10, 2) NOT NULL,
    payment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

-- 8. Customers Table (Frequent Users - Core entity)
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    vehicle_plate VARCHAR(20) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8.1 Customer Phones Table (Normalization: 1NF Separation for multi-valued attribute)
-- Solves the multi-valued attribute problem where a single customer can have multiple phone numbers.
CREATE TABLE customer_phones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- 9. Audit Log Table (Demonstrates Durability & Traceability)
CREATE TABLE system_audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(50),
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- CONCURRENCY AND TRIGGERS
-- ==========================================

-- TRIGGER 1: Automatic Audit Logging for Entry
DELIMITER //
CREATE TRIGGER after_parking_entry
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    INSERT INTO system_audit_log (action_type, details)
    VALUES ('VEHICLE_ENTRY', CONCAT('Vehicle ', NEW.vehicle_plate, ' entered spot ID ', NEW.spot_id));
END //
DELIMITER ;

-- TRIGGER 2: Automatic Audit Logging for Exit
DELIMITER //
CREATE TRIGGER after_parking_exit
AFTER UPDATE ON transactions
FOR EACH ROW
BEGIN
    IF OLD.exit_time IS NULL AND NEW.exit_time IS NOT NULL THEN
        INSERT INTO system_audit_log (action_type, details)
        VALUES ('VEHICLE_EXIT', CONCAT('Vehicle ', NEW.vehicle_plate, ' exited. Fee: $', NEW.fee));
    END IF;
END //
DELIMITER ;

-- VIEW: Dashboard Summary (Demonstrates Data Abstraction)
CREATE OR REPLACE VIEW dashboard_overview AS
SELECT 
    s.spot_number, 
    v.type_name, 
    z.zone_name,
    s.is_occupied, 
    s.vehicle_plate
FROM parking_spots s
JOIN vehicle_types v ON s.type_id = v.id
JOIN parking_zones z ON s.zone_id = z.id;

-- ==========================================
-- SEED DATA 
-- ==========================================

INSERT INTO users (username, password, role) VALUES 
('admin', 'admin123', 'admin'),
('dipak', 'abc', 'operator');

INSERT INTO vehicle_types (type_name, hourly_rate) VALUES 
('Car', 5.00), ('Bike', 2.00), ('Truck', 10.00);

INSERT INTO parking_zones (zone_name, description) VALUES 
('VIP - Ground', 'Ground floor near entrance'), 
('Level 1 - Cars', 'First floor car parking'),
('Level 2 - Bikes', 'Second floor two-wheeler parking');

-- Insert initial VIP spots (20 spots)
INSERT INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('V-01', 1, 1), ('V-02', 1, 1), ('V-03', 1, 1), ('V-04', 1, 1), ('V-05', 1, 1),
('V-06', 1, 1), ('V-07', 1, 1), ('V-08', 1, 1), ('V-09', 1, 1), ('V-10', 1, 1),
('V-11', 1, 1), ('V-12', 1, 1), ('V-13', 1, 1), ('V-14', 1, 1), ('V-15', 1, 1),
('V-16', 1, 1), ('V-17', 1, 1), ('V-18', 1, 1), ('V-19', 1, 1), ('V-20', 1, 1);

-- Insert initial Level 1 spots (20 spots)
INSERT INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('L1-01', 2, 1), ('L1-02', 2, 1), ('L1-03', 2, 1), ('L1-04', 2, 1), ('L1-05', 2, 1),
('L1-06', 2, 1), ('L1-07', 2, 1), ('L1-08', 2, 1), ('L1-09', 2, 1), ('L1-10', 2, 1),
('L1-11', 2, 1), ('L1-12', 2, 1), ('L1-13', 2, 1), ('L1-14', 2, 1), ('L1-15', 2, 1),
('L1-16', 2, 1), ('L1-17', 2, 1), ('L1-18', 2, 1), ('L1-19', 2, 1), ('L1-20', 2, 1);

-- Insert initial Level 2 spots (20 spots)
INSERT INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('B-01', 3, 2), ('B-02', 3, 2), ('B-03', 3, 2), ('B-04', 3, 2), ('B-05', 3, 2),
('B-06', 3, 2), ('B-07', 3, 2), ('B-08', 3, 2), ('B-09', 3, 2), ('B-10', 3, 2),
('B-11', 3, 2), ('B-12', 3, 2), ('B-13', 3, 2), ('B-14', 3, 2), ('B-15', 3, 2),
('B-16', 3, 2), ('B-17', 3, 2), ('B-18', 3, 2), ('B-19', 3, 2), ('B-20', 3, 2);

INSERT INTO monthly_passes (vehicle_plate, owner_name, valid_until) VALUES 
('VIP-1111', 'Rajeev Kumar', '2027-12-31');

INSERT INTO customers (customer_code, name, vehicle_plate) VALUES 
('CUST-001', 'Rahul Sharma', 'MH12AB1001'),
('CUST-002', 'Priya Patel', 'MH14XY2002'),
('CUST-003', 'Aarav Singh', 'KA01CD3003'),
('CUST-004', 'Neha Gupta', 'DL10CZ5432');

INSERT INTO customer_phones (customer_id, phone_number) VALUES 
(1, '9876543210'),
(1, '8976543210'),
(2, '7890123456'),
(3, '9812345678'),
(3, '8812345678'),
(4, '9998887776');

-- ==========================================
-- SIMULATE LIVE OCCUPIED SPOTS
-- ==========================================

-- Rahul Sharma is parked in VIP spot V-02
UPDATE parking_spots SET is_occupied = TRUE, vehicle_plate = 'MH12AB1001' WHERE spot_number = 'V-02';
INSERT INTO transactions (vehicle_plate, spot_id, entry_time) SELECT 'MH12AB1001', spot_id, DATE_SUB(NOW(), INTERVAL 3 HOUR) FROM parking_spots WHERE spot_number = 'V-02';

-- Random Guest is parked in Level 1 spot L1-05
UPDATE parking_spots SET is_occupied = TRUE, vehicle_plate = 'DL01AA8899' WHERE spot_number = 'L1-05';
INSERT INTO transactions (vehicle_plate, spot_id, entry_time) SELECT 'DL01AA8899', spot_id, DATE_SUB(NOW(), INTERVAL 5 HOUR) FROM parking_spots WHERE spot_number = 'L1-05';

-- Aarav Singh is parked in Level 2 spot B-10 (Bike)
UPDATE parking_spots SET is_occupied = TRUE, vehicle_plate = 'KA01CD3003' WHERE spot_number = 'B-10';
INSERT INTO transactions (vehicle_plate, spot_id, entry_time) SELECT 'KA01CD3003', spot_id, DATE_SUB(NOW(), INTERVAL 1 HOUR) FROM parking_spots WHERE spot_number = 'B-10';