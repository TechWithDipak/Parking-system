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