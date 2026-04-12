DROP DATABASE IF EXISTS parking_sys;
CREATE DATABASE parking_sys;
USE parking_sys;

-- ==========================================
-- ADVANCED DBMS SCHEMA FOR REVIEW 3
-- Fully Normalized up to 5NF (PJNF)
-- ==========================================

-- 1. Users Table (Authentication)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- 2. Vehicle Types Table (3NF Separation)
CREATE TABLE vehicle_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(20) NOT NULL UNIQUE,
    hourly_rate DECIMAL(5, 2) NOT NULL CHECK (hourly_rate >= 0)
);

-- 3. Parking Zones Table (3NF Location mapping)
CREATE TABLE parking_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

-- 4. Parking Spots Table (BCNF compliant)
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

-- 5. Monthly Passes Table
CREATE TABLE monthly_passes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_plate VARCHAR(20) NOT NULL UNIQUE,
    owner_name VARCHAR(50) NOT NULL,
    valid_until DATE NOT NULL
);

-- ==========================================
-- 4NF DECOMPOSITION: Independent Multi-Valued Attributes
-- Problem: A customer can have multiple phones AND multiple vehicles. 
-- Solution: Decompose into 3 independent tables to eliminate Multi-Valued Dependencies (MVDs).
-- ==========================================
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer_phones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE TABLE customer_vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    vehicle_plate VARCHAR(20) NOT NULL UNIQUE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- ==========================================
-- 5NF DECOMPOSITION: Project-Join Normal Form (PJNF)
-- Problem: Ternary relationship (User, Zone, Shift) where cyclic join dependencies exist.
-- Solution: Decompose into 3 binary tables to eliminate Join Anomalies.
-- ==========================================
CREATE TABLE shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shift_name VARCHAR(20) NOT NULL UNIQUE -- e.g., Morning, Night
);

-- Binary 1: Which Operator is authorized for which Zone?
CREATE TABLE operator_zones (
    user_id INT NOT NULL,
    zone_id INT NOT NULL,
    PRIMARY KEY (user_id, zone_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id) REFERENCES parking_zones(id) ON DELETE CASCADE
);

-- Binary 2: Which Operator is assigned to which Shift?
CREATE TABLE operator_shifts (
    user_id INT NOT NULL,
    shift_id INT NOT NULL,
    PRIMARY KEY (user_id, shift_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE CASCADE
);

-- Binary 3: Which Zone requires which Shift?
CREATE TABLE zone_shifts (
    zone_id INT NOT NULL,
    shift_id INT NOT NULL,
    PRIMARY KEY (zone_id, shift_id),
    FOREIGN KEY (zone_id) REFERENCES parking_zones(id) ON DELETE CASCADE,
    FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE CASCADE
);

-- ==========================================
-- CORE FUNCTIONAL TABLES (Transactions)
-- ==========================================
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_plate VARCHAR(20) NOT NULL,
    spot_id INT NOT NULL,
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    exit_time DATETIME DEFAULT NULL,
    fee DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (spot_id) REFERENCES parking_spots(spot_id) ON DELETE RESTRICT
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
);

CREATE TABLE system_audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(50),
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- TRIGGERS
-- ==========================================

DELIMITER //
CREATE TRIGGER after_parking_entry
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    INSERT INTO system_audit_log (action_type, details)
    VALUES ('VEHICLE_ENTRY', CONCAT('Vehicle ', NEW.vehicle_plate, ' entered spot ID ', NEW.spot_id));
END //
DELIMITER ;

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

-- ==========================================
-- LIVE DBMS SEED DATA
-- ==========================================

INSERT INTO users (username, password) VALUES 
('admin', 'admin123'), ('dipak', 'abc');

INSERT INTO shifts (shift_name) VALUES ('Morning'), ('Evening'), ('Night');

INSERT INTO vehicle_types (type_name, hourly_rate) VALUES 
('Car', 5.00), ('Bike', 2.00), ('Truck', 10.00);

INSERT INTO parking_zones (zone_name, description) VALUES 
('VIP - Ground', 'Ground floor near entrance'), 
('Level 1 - Cars', 'First floor car parking'),
('Level 2 - Bikes', 'Second floor two-wheeler parking');

-- Insert spots for VIP (25 spots)
INSERT INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('V-01', 1, 1), ('V-02', 1, 1), ('V-03', 1, 1), ('V-04', 1, 1), ('V-05', 1, 1),
('V-06', 1, 1), ('V-07', 1, 1), ('V-08', 1, 1), ('V-09', 1, 1), ('V-10', 1, 1),
('V-11', 1, 1), ('V-12', 1, 1), ('V-13', 1, 1), ('V-14', 1, 1), ('V-15', 1, 1),
('V-16', 1, 1), ('V-17', 1, 1), ('V-18', 1, 1), ('V-19', 1, 1), ('V-20', 1, 1),
('V-21', 1, 1), ('V-22', 1, 1), ('V-23', 1, 1), ('V-24', 1, 1), ('V-25', 1, 1);

-- Insert spots for Level 1 - Cars (25 spots)
INSERT INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('L1-01', 2, 1), ('L1-02', 2, 1), ('L1-03', 2, 1), ('L1-04', 2, 1), ('L1-05', 2, 1),
('L1-06', 2, 1), ('L1-07', 2, 1), ('L1-08', 2, 1), ('L1-09', 2, 1), ('L1-10', 2, 1),
('L1-11', 2, 1), ('L1-12', 2, 1), ('L1-13', 2, 1), ('L1-14', 2, 1), ('L1-15', 2, 1),
('L1-16', 2, 1), ('L1-17', 2, 1), ('L1-18', 2, 1), ('L1-19', 2, 1), ('L1-20', 2, 1),
('L1-21', 2, 1), ('L1-22', 2, 1), ('L1-23', 2, 1), ('L1-24', 2, 1), ('L1-25', 2, 1);

-- Insert spots for Level 2 - Bikes (25 spots)
INSERT INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('B-01', 3, 2), ('B-02', 3, 2), ('B-03', 3, 2), ('B-04', 3, 2), ('B-05', 3, 2),
('B-06', 3, 2), ('B-07', 3, 2), ('B-08', 3, 2), ('B-09', 3, 2), ('B-10', 3, 2),
('B-11', 3, 2), ('B-12', 3, 2), ('B-13', 3, 2), ('B-14', 3, 2), ('B-15', 3, 2),
('B-16', 3, 2), ('B-17', 3, 2), ('B-18', 3, 2), ('B-19', 3, 2), ('B-20', 3, 2),
('B-21', 3, 2), ('B-22', 3, 2), ('B-23', 3, 2), ('B-24', 3, 2), ('B-25', 3, 2);

-- Seed 4NF data
INSERT INTO customers (customer_code, name) VALUES 
('CUST-001', 'Rahul Sharma'), ('CUST-002', 'Priya Patel'), ('CUST-003', 'Aarav Singh');

INSERT INTO customer_phones (customer_id, phone_number) VALUES 
(1, '9876543210'), (1, '8976543210'), (2, '7890123456');

INSERT INTO customer_vehicles (customer_id, vehicle_plate) VALUES 
(1, 'MH12AB1001'), (1, 'MH12AB1002'), (2, 'MH14XY2002'), (3, 'KA01CD3003');

-- Seed 5NF data (PJNF implies an Operator is placed if all binary pairs align)
INSERT INTO operator_zones (user_id, zone_id) VALUES (2, 1), (2, 2);
INSERT INTO operator_shifts (user_id, shift_id) VALUES (2, 1);
INSERT INTO zone_shifts (zone_id, shift_id) VALUES (1, 1), (2, 1);

-- Occupy a spot
UPDATE parking_spots SET is_occupied = TRUE, vehicle_plate = 'MH12AB1001' WHERE spot_number = 'V-02';
INSERT INTO transactions (vehicle_plate, spot_id, entry_time) SELECT 'MH12AB1001', spot_id, DATE_SUB(NOW(), INTERVAL 3 HOUR) FROM parking_spots WHERE spot_number = 'V-02';
