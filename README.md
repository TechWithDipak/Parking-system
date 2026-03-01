# 🚗 Car Parking Management System (Pro Max)

A robust, full-stack web application designed to automate and manage parking lot operations. This advanced system manages real-time tracking of parking spots across multiple zones, vehicle entry/exit logging, automated fee calculation, customer management, and role-based access control.

---

## ✨ Key Features

### 📊 Real-time Dashboard
- Visual grid representation of all parking slots  
- Live occupancy updates  
- Handles up to **25 spots per level** seamlessly  
- Zone-based layout support (VIP, Level 1, etc.)

### 👥 Customer Management
- Register frequent customers with unique IDs  
- Auto-fill registered license plate during check-in  
- Linked customer history and transaction tracking  

### 🧾 Smart Check-Out Modal
- Interactive pop-up before finalizing checkout  
- Automatically calculates:
  - Total parking duration  
  - Applicable rate  
  - Final payable amount  

### 💰 Dynamic Pricing Engine
- Hourly pricing based on vehicle type:
  - 🚗 Car  
  - 🏍️ Bike  
  - 🚚 Truck  

### 🗓️ Monthly Pass Detection
- Automatically verifies active monthly subscriptions  
- If valid → Parking fee is **$0.00**  
- Seamless subscription handling  

### 📑 Transaction & Payment Logs
- Dedicated history page  
- Complete record of:
  - Entry time  
  - Exit time  
  - Duration  
  - Vehicle type  
  - Payment method (Cash / Card / UPI)  

### 📱 Responsive UI
- Built with **Tailwind CSS**  
- Clean, modern design  
- Fully responsive across devices  

---

## 🛠️ Technology Stack

**Backend**
- Python 3  
- Flask  

**Frontend**
- HTML5  
- Tailwind CSS  
- JavaScript  
- FontAwesome Icons  

**Database**
- MySQL  

**Database Driver**
- mysql-connector-python  

---

## 🗄️ Database Architecture (8 Tables)

The system follows a normalized relational schema.

| Table Name       | Description |
|------------------|-------------|
| `users`          | Stores system admins and operators |
| `vehicle_types`  | Base pricing configuration |
| `parking_zones`  | Logical/physical parking areas |
| `parking_spots`  | Individual slots linked to zones |
| `monthly_passes` | Subscription tracking |
| `transactions`   | Core entry/exit logs |
| `payments`       | Financial records tied to transactions |
| `customers`      | Registered frequent users |

---

## 🚀 Installation & Setup Guide

### 1️⃣ Prerequisites

Ensure the following are installed:

- Python 3.8+
- MySQL Community Edition

---

### 2️⃣ Database Initialization

1. Open MySQL Workbench or Terminal.
2. Execute the `schema.sql` file to:
   - Create the `parking_sys` database
   - Create all 8 tables
   - Insert seed data (zones, spots, default users)

---

### 3️⃣ Application Setup

Navigate to the project directory and execute:

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv

# 2. Activate the virtual environment

# Windows:
.\venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install flask mysql-connector-python