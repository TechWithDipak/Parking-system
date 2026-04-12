# DBMS Review 3 Report: Normalization, Transactions & Concurrency

This document is structurally designed to assist you in defending your project during the "Review 3" viva. It includes all major functional aspects from the system morning implementation in addition to the newly added normalization of multi-valued attributes in the database.

---

## 1. Normalization (Adding Multi-Valued Attributes & Normalizing)

**Why was this done?** 
In a viva, you might be asked to demonstrate how you handled a **1NF (First Normal Form) violation**, specifically regarding **multi-valued attributes**. A classic example is a customer possessing multiple phone numbers.

### BEFORE Normalization (The Problem)
If we attempted to store multiple phone numbers in the `customers` table, it would violate 1NF because the data would no longer be atomic (a single cell would contain multiple values).

**Unnormalized `customers` Table (Violates 1NF):**
| id | customer_code | name        | vehicle_plate | phone_numbers (Multi-Valued) |
|----|---------------|-------------|---------------|------------------------------|
| 1  | CUST-001      | Alice Smith | MH12AB1001    | 555-0101, 555-0102       |
| 2  | CUST-002      | Bob Jones   | MH14XY2002    | 555-0201                     |

- *Anomaly:* Difficult to query a specific phone number. You can't easily index or delete a single phone number without messy string manipulation.

### AFTER Normalization (The Solution - 1NF Achieved)
To resolve this mapping issue, we removed the multi-valued attribute from the `customers` table and created a new linked table called `customer_phones`.

**Normalized `customers` Table:**
| id | customer_code | name        | vehicle_plate |
|----|---------------|-------------|---------------|
| 1  | CUST-001      | Alice Smith | MH12AB1001    |
| 2  | CUST-002      | Bob Jones   | MH14XY2002    |

**New `customer_phones` Table:**
| id | customer_id (FK) | phone_number |
|----|------------------|--------------|
| 1  | 1                | 555-0101     |
| 2  | 1                | 555-0102     |
| 3  | 2                | 555-0201     |

**Code Changes for this:**
1. **Frontend (`app.py` UI):** Added an input field for "Phone Numbers (Comma separated)" indicating the 1NF context. During the template rendering, we adjusted the SQL query using `GROUP_CONCAT` and `LEFT JOIN` to group the discrete phone numbers purely to display them gracefully without violating DB structure.
2. **Backend (`app.py` Route):** Processed the input string, split it into a list, and executed multiple atomic `INSERT INTO customer_phones` queries tied to the newly generated `customer_id`.
3. **Database (`schema.sql`):** Separated `customers` and `customer_phones`. We used `ON DELETE CASCADE` so deleting a customer auto-cleans their phone numbers.

*(Note: We also already implemented 2NF and 3NF by extracting `hourly_rates` into `vehicle_types` and `zone_names` into `parking_zones` previously!)*

---

## 2. Transaction Management (ACID Properties)

**Where is it?** Look in `app.py`, specifically the `/park` and `/exit` routes.

During the morning session, we properly incorporated Transaction Management so you can confidently answer the ACID rubric:

1.  **Atomicity ("All or Nothing"):** In the `/park` logic, inserting the `transaction` record and updating the `parking_spots` record is encapsulated inside an explicit transaction block (`conn.start_transaction()`). If something fails, we catch the exception and run `conn.rollback()` so partial records don't persist. If it works, we heavily rely on `conn.commit()`.
2.  **Consistency:** The system enforces check constraints (like `hourly_rate >= 0`), foreign keys, and unique constraints. A transaction guarantees leaving the database in a valid state.
3.  **Isolation (Concurrency):** Concurrent transactions are protected using row-level and table-level locks (see Section 3).
4.  **Durability:** Data changes are pushed permanently to the disk. Plus, our `system_audit_log` with MySQL Triggers (`after_parking_entry` / `after_parking_exit`) makes sure operations natively persist history even if the frontend crashes.

---

## 3. Concurrency Control & Locking Mechanisms

**Where is it?** Check the `/api/calculate_fee`, `/park`, and `/reports` routes.

This is a specific request in the Review 3 rubric. You must prove you demonstrated locking.

*   **Row-Level Shared Lock (`SELECT ... FOR SHARE`)**:
    *   *Where:* In the `/api/calculate_fee/<spot_id>` API route used when calculating ticket prices for the modal.
    *   *Why:* When calculating the fare, we get a Shared Lock. Other staff members can still READ the data (e.g. check history), but *nobody can update or modify* the transaction/spot rate until calculating is securely completed.

*   **Row-Level Exclusive Lock (`SELECT ... FOR UPDATE`)**:
    *   *Where:* In the `/park` (check-in) and `/exit` (check-out) routes.
    *   *Why:* While issuing a spot or completing an exit, we demand an exclusive lock right away (`SELECT is_occupied FROM parking_spots WHERE spot_id = %s FOR UPDATE`). If two operators try to assign the identical spot at the same microsecond, one will block until the first finishes, avoiding double-bookings.

*   **Table-Level Shared & Exclusive Locks (`LOCK TABLES READ / WRITE`)**:
    *   *Where:* In the `/reports` route.
    *   *Why:* Generating the financial summary. We perform `LOCK TABLES payments READ, system_audit_log WRITE, users READ`. This provides guaranteed complete table-snapshot isolation meaning no new payments can sneak into the results while we are aggregating totals!
