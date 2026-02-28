DROP DATABASE IF EXISTS parking_sys;
CREATE DATABASE parking_sys;
USE parking_sys;

-- 1. Users Table (Authentication)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator'
);

-- 2. Vehicle Types Table (Pricing strategy)
CREATE TABLE vehicle_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(20) NOT NULL UNIQUE,
    hourly_rate DECIMAL(5, 2) NOT NULL
);

-- 3. Parking Zones Table (Location mapping)
CREATE TABLE parking_zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

-- 4. Parking Spots Table (Physical slots)
CREATE TABLE parking_spots (
    spot_id INT AUTO_INCREMENT PRIMARY KEY,
    spot_number VARCHAR(10) NOT NULL UNIQUE,
    zone_id INT NOT NULL,
    type_id INT NOT NULL,
    is_occupied BOOLEAN DEFAULT FALSE,
    vehicle_plate VARCHAR(20) DEFAULT NULL,
    FOREIGN KEY (zone_id) REFERENCES parking_zones(id),
    FOREIGN KEY (type_id) REFERENCES vehicle_types(id)
);

-- 5. Monthly Passes Table (Subscriptions)
CREATE TABLE monthly_passes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_plate VARCHAR(20) NOT NULL UNIQUE,
    owner_name VARCHAR(50) NOT NULL,
    valid_until DATE NOT NULL
);

-- 6. Transactions Table (Log of entry and exit)
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_plate VARCHAR(20) NOT NULL,
    spot_id INT NOT NULL,
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    exit_time DATETIME DEFAULT NULL,
    fee DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (spot_id) REFERENCES parking_spots(spot_id)
);

-- 7. Payments Table (Financial records)
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    payment_method VARCHAR(20) NOT NULL, -- Cash, Card, UPI, Pass
    amount DECIMAL(10, 2) NOT NULL,
    payment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);


-- ==========================================
-- SEED DATA (Test Data to get you started)
-- ==========================================

-- Insert Users
INSERT INTO users (username, password, role) VALUES 
('admin', 'admin123', 'admin'),
('dipak', 'abc', 'operator');

-- Insert Vehicle Types
INSERT INTO vehicle_types (type_name, hourly_rate) VALUES 
('Car', 5.00), ('Bike', 2.00), ('Truck', 10.00);

-- Insert Parking Zones
INSERT INTO parking_zones (zone_name, description) VALUES 
('VIP - Ground', 'Ground floor near entrance'), 
('Level 1 - Cars', 'First floor car parking'),
('Level 2 - Bikes', 'Second floor two-wheeler parking');

-- Create spots linked to zones and types
INSERT INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('V-01', 1, 1), ('V-02', 1, 1), -- VIP Cars
('L1-01', 2, 1), ('L1-02', 2, 1), ('L1-03', 2, 1), -- Normal Cars
('B-01', 3, 2), ('B-02', 3, 2), ('B-03', 3, 2); -- Bikes

-- Create a monthly pass (Valid till 2027)
INSERT INTO monthly_passes (vehicle_plate, owner_name, valid_until) VALUES 
('VIP-1111', 'John Doe', '2027-12-31');

USE parking_sys;

-- 1. Create the new Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    vehicle_plate VARCHAR(20) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Insert Test Customers
INSERT INTO customers (customer_code, name, vehicle_plate) VALUES 
('CUST-001', 'Alice Smith', 'MH12AB1001'),
('CUST-002', 'Bob Jones', 'MH14XY2002'),
('CUST-003', 'Charlie Brown', 'KA01CD3003');

-- 3. Add 20 spots to VIP Zone (zone_id=1, type_id=1)
INSERT IGNORE INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('V-03', 1, 1), ('V-04', 1, 1), ('V-05', 1, 1), ('V-06', 1, 1), ('V-07', 1, 1),
('V-08', 1, 1), ('V-09', 1, 1), ('V-10', 1, 1), ('V-11', 1, 1), ('V-12', 1, 1),
('V-13', 1, 1), ('V-14', 1, 1), ('V-15', 1, 1), ('V-16', 1, 1), ('V-17', 1, 1),
('V-18', 1, 1), ('V-19', 1, 1), ('V-20', 1, 1), ('V-21', 1, 1), ('V-22', 1, 1);

-- 4. Add 20 spots to Level 1 - Cars (zone_id=2, type_id=1)
INSERT IGNORE INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('L1-04', 2, 1), ('L1-05', 2, 1), ('L1-06', 2, 1), ('L1-07', 2, 1), ('L1-08', 2, 1),
('L1-09', 2, 1), ('L1-10', 2, 1), ('L1-11', 2, 1), ('L1-12', 2, 1), ('L1-13', 2, 1),
('L1-14', 2, 1), ('L1-15', 2, 1), ('L1-16', 2, 1), ('L1-17', 2, 1), ('L1-18', 2, 1),
('L1-19', 2, 1), ('L1-20', 2, 1), ('L1-21', 2, 1), ('L1-22', 2, 1), ('L1-23', 2, 1);

-- 5. Add 20 spots to Level 2 - Bikes (zone_id=3, type_id=2)
INSERT IGNORE INTO parking_spots (spot_number, zone_id, type_id) VALUES 
('B-04', 3, 2), ('B-05', 3, 2), ('B-06', 3, 2), ('B-07', 3, 2), ('B-08', 3, 2),
('B-09', 3, 2), ('B-10', 3, 2), ('B-11', 3, 2), ('B-12', 3, 2), ('B-13', 3, 2),
('B-14', 3, 2), ('B-15', 3, 2), ('B-16', 3, 2), ('B-17', 3, 2), ('B-18', 3, 2),
('B-19', 3, 2), ('B-20', 3, 2), ('B-21', 3, 2), ('B-22', 3, 2), ('B-23', 3, 2);