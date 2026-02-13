
CREATE DATABASE IF NOT EXISTS parking_sys;
USE parking_sys;


CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, 
    role VARCHAR(20) DEFAULT 'operator'
);


CREATE TABLE IF NOT EXISTS parking_spots (
    spot_id INT AUTO_INCREMENT PRIMARY KEY,
    spot_number VARCHAR(10) NOT NULL UNIQUE,
    is_occupied BOOLEAN DEFAULT FALSE,
    vehicle_plate VARCHAR(20) DEFAULT NULL
);


CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_plate VARCHAR(20),
    spot_id INT,
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    exit_time DATETIME DEFAULT NULL,
    fee DECIMAL(10, 2) DEFAULT 0.00
);


INSERT IGNORE INTO parking_spots (spot_number) VALUES 
('A1'), ('A2'), ('A3'), ('A4'), ('A5'),
('B1'), ('B2'), ('B3'), ('B4'), ('B5');


INSERT IGNORE INTO users (username, password, role) 
VALUES ('admin', 'admin123', 'admin');