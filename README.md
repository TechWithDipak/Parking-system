🚗 Car Parking Management System (Pro Max)

A robust, full-stack web application designed to automate and manage parking lot operations. This advanced system handles real-time tracking of parking spots across multiple zones, vehicle entry/exit logging, automated fee calculation, customer management, and role-based access.

✨ Key Features

Real-time Dashboard: Visual grid representation of all parking slots with live occupancy status, handling up to 25 spots per level seamlessly.

Customer Management: Register frequent customers with unique IDs. Selecting a customer during check-in automatically auto-fills their registered license plate.

Smart Check-Out Modal: An interactive pop-up that calculates and displays the exact parking duration and fee before finalizing the checkout.

Dynamic Pricing: Hourly rates adjust automatically based on the vehicle type (Car, Bike, Truck).

Monthly Passes: The system automatically detects if a vehicle has an active monthly pass and waives the parking fee ($0.00).

Transaction & Payment Logs: A dedicated history page to view all past parking sessions, including the payment method used (Cash, Card, UPI).

Responsive UI: A modern, clean interface built with Tailwind CSS that adapts to different screen sizes.

🛠️ Technology Stack

Backend: Python 3, Flask framework

Frontend: HTML5, Tailwind CSS, JavaScript, FontAwesome Icons

Database: MySQL

Database Driver: mysql-connector-python

🗄️ Database Architecture (8 Tables)

The system is highly normalized and utilizes the following tables:

users: System administrators and operators.

vehicle_types: Base pricing rules (e.g., Cars vs. Bikes).

parking_zones: Physical layout areas (e.g., VIP, Level 1).

parking_spots: Individual parking slots tied to zones and types.

monthly_passes: Active subscription tracking.

transactions: Core log of every vehicle entry and exit.

payments: Financial records tied to transactions.

customers: Registered frequent parkers with pre-linked license plates.

🚀 Installation & Setup Guide

1. Prerequisites

Ensure you have the following installed on your machine:

Python 3.8+

[suspicious link removed] (Community Edition)

2. Database Initialization

Open your MySQL client (Workbench or Terminal).

Execute your schema.sql script to create the parking_sys database, the 8 tables, and insert the seed data (spots, zones, and default users).

3. Application Setup

Open your terminal in the project directory and run the following commands:

# 1. Create a virtual environment (optional but recommended)
python -m venv venv

# 2. Activate the virtual environment
# On Windows:
.\\venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install required Python packages
pip install flask mysql-connector-python


4. Configuration

Open app.py in your code editor.

Locate the db_config dictionary at the top of the file.

Change the 'password' field to match your actual local MySQL root password.

5. Run the Application

Start the Flask development server:

python app.py


Open your web browser and navigate to: https://www.google.com/search?q=http://127.0.0.1:5000

🔐 Default Credentials

Use these credentials to log in for the first time (as configured in the seed data):

Username: admin

Password: admin123

Role: Admin

Developed as a Database Management System (DBMS) Project.