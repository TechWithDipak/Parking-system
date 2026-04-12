# Normalization & Functional Dependencies Report

## 1. Anomalies Identified in Initial Unnormalized State
If we had a single massive table (e.g., `Parking_Data`), we would suffer from the following anomalies:
*   **Insertion Anomaly:** We cannot add a new vehicle type/pricing without first having a parking spot or a vehicle parked.
*   **Deletion Anomaly:** If a customer deletes their parking transaction, the system might lose data about the parking zone or the vehicle hourly rate if no other vehicle of that type is parked.
*   **Update Anomaly:** If the hourly rate for "Car" changes, every single record in the transactions table for a "Car" would need to be updated simultaneously to maintain consistency.

## 2. Functional Dependencies (FDs)
Based on business rules, we identified the following FDs:
*   `spot_id` → `spot_number`, `zone_id`, `type_id`, `is_occupied`, `vehicle_plate`
*   `type_id` → `type_name`, `hourly_rate`
*   `zone_id` → `zone_name`, `description`
*   `transaction_id` → `vehicle_plate`, `spot_id`, `entry_time`, `exit_time`, `fee`
*   `customer_code` → `name`, `vehicle_plate`

## 3. Normalization Process (Up to 3NF)

### 1st Normal Form (1NF)
*   **Rule:** Eliminate repeating groups/arrays. All attributes must be atomic.
*   **Implementation:** All tables (`users`, `vehicle_types`, `parking_zones`, `parking_spots`, `transactions`, `customers`) have completely atomic data types. There are no comma-separated lists of values (e.g., no single column containing multiple `vehicle_plates`).

### 2nd Normal Form (2NF)
*   **Rule:** Must be in 1NF, and no non-prime attribute is dependent on a proper subset of any candidate key (no partial dependencies).
*   **Implementation:** Every table has a single-column Primary Key (like `id` or `spot_id`). Since primary keys are not composite, partial dependencies are inherently impossible. All non-key columns depend on the **entire** Primary Key.

### 3rd Normal Form (3NF)
*   **Rule:** Must be in 2NF, and no non-prime attribute is transitively dependent on the primary key. Every non-prime attribute must depend *only* on the candidate keys. ("The key, the whole key, and nothing but the key".)
*   **Implementation:**
    *   **Separation of Pricing:** We moved `hourly_rate` and `type_name` into the `vehicle_types` table. If these were in `parking_spots`, they would depend transitively on `type_id`, violating 3NF.
    *   **Separation of Zones:** `zone_name` and `description` are in `parking_zones`.
    *   **Separation of Payments:** The `payments` table separates financial records from pure `transactions`.
    *   All tables proudly adhere to 3NF.
