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

-- 8. Customers Table (Frequent Users)
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    vehicle_plate VARCHAR(20) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

-- Insert initial VIP spots
INSERT INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('V-01', 1, 1), ('V-02', 1, 1), ('V-03', 1, 1), ('V-04', 1, 1), ('V-05', 1, 1),
('V-06', 1, 1), ('V-07', 1, 1), ('V-08', 1, 1), ('V-09', 1, 1), ('V-10', 1, 1);

-- Insert initial Level 1 spots
INSERT INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('L1-01', 2, 1), ('L1-02', 2, 1), ('L1-03', 2, 1), ('L1-04', 2, 1), ('L1-05', 2, 1),
('L1-06', 2, 1), ('L1-07', 2, 1), ('L1-08', 2, 1), ('L1-09', 2, 1), ('L1-10', 2, 1);

-- Insert initial Level 2 spots
INSERT INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('B-01', 3, 2), ('B-02', 3, 2), ('B-03', 3, 2), ('B-04', 3, 2), ('B-05', 3, 2),
('B-06', 3, 2), ('B-07', 3, 2), ('B-08', 3, 2), ('B-09', 3, 2), ('B-10', 3, 2);

INSERT INTO monthly_passes (vehicle_plate, owner_name, valid_until) VALUES 
('VIP-1111', 'John Doe', '2027-12-31');

INSERT INTO customers (customer_code, name, vehicle_plate) VALUES 
('CUST-001', 'Alice Smith', 'MH12AB1001'),
('CUST-002', 'Bob Jones', 'MH14XY2002'),
('CUST-003', 'Charlie Brown', 'KA01CD3003');