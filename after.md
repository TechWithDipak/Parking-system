# Relational Database Normalization Report (1NF to 5NF)

This comprehensive defense document details the step-by-step rigorous process taken to normalize the Car Parking Management System database from its initial 1st Normal Form (1NF) implementation up to the advanced 5th Normal Form (5NF / Project-Join Normal Form).

**Objective:** To ensure **Lossless Join Decompositions** and strict **Dependency Preservation**, guaranteeing zero update, insertion, or deletion anomalies. 

---

## The "Before" State: Anatomy of Anomalies
Initially, the database consisted of broad, multi-purpose tables. A theoretical unnormalized `customer_details` table looked like this:
*   `customer_details (customer_id, name, phones, vehicle_plates, zone_assigned, shift_assigned)`

**Anomalies Present:**
1.  **Insertion Anomaly:** We could not add a new `shift` without an active `customer` parking in a `zone`.
2.  **Update Anomaly:** Updating a customer's `name` would require updating multiple rows if they drove multiple `vehicle_plates`.
3.  **Deletion Anomaly:** Deleting a specific `vehicle_plate` record might wipe out the only record of the customer's `phone` number completely.

---

## Step-by-Step Normalization Proof

### 1. First Normal Form (1NF)
**Rule:** A relation is in 1NF if all attributes are domain atomic (no multi-valued attributes or repeating groups).
**Action:** We detected that `phones` (e.g. "9876543210, 8976543210") violated domain constraints. 

**Before 1NF:**
| customer_id | name | phones |
| :--- | :--- | :--- |
| 1 | Dipak Kumar | 9876543210, 8976543210 |

**Implementation:** Created two tables, where the phone attribute became separated. Both tables now contain only single, scalar values per cell.

**After 1NF:**
*Table: `customers`*
| customer_id | name |
| :--- | :--- |
| 1 | Dipak Kumar |

*Table: `customer_phones`*
| customer_id | phone_number |
| :--- | :--- |
| 1 | 9876543210 |
| 1 | 8976543210 |

### 2. Second Normal Form (2NF)
**Rule:** It is in 1NF and no non-prime attribute is dependent on any proper subset of any candidate key (Partial Dependency).
**Action:** Our tables like `parking_spots` rely on a single-column primary key (`spot_id`). Because the primary key is inherently a single attribute (atomic), partial dependencies simply cannot mathematically exist. All tables inherently satisfy 2NF constraints.

**Before 2NF (Hypothetical Violation for Demo):**
If we used a composite key of `(zone_id, type_id)` mapped to `zone_name`, `zone_name` is only dependent on `zone_id` (a partial dependency).
| zone_id (PK) | type_id (PK) | zone_name | hourly_rate |
| :--- | :--- | :--- | :--- |
| Z1 | T1 | North Zone | 50.00 |
| Z1 | T2 | North Zone | 20.00 |

**After 2NF:**
By utilizing single-attribute surrogate and primary keys across our schema, we eliminated any chance of partial dependencies.
*Table: `parking_zones` (Fully dependent on `id`)*
| id | zone_name |
| :--- | :--- |
| Z1 | North Zone |

### 3. Third Normal Form (3NF)
**Rule:** It is in 2NF, and no non-prime attribute is transitively dependent on the primary key.
**Action:** The `parking_spots` originally housed `hourly_rate` and `zone_name`. 
*   **FD:** `spot_id` → `type_id` → `hourly_rate`
*   **FD:** `spot_id` → `zone_id` → `zone_name`
This represents a classic transitive dependency! 

**Before 3NF:**
| spot_id | zone_id | zone_name | type_id | hourly_rate |
| :--- | :--- | :--- | :--- | :--- |
| S101 | Z1 | North Zone | T1 | 50.00 |
| S102 | Z1 | North Zone | T1 | 50.00 |

**Implementation:** Decomposed `parking_spots` into `vehicle_types` and `parking_zones` (Retaining FK constraints).

**After 3NF:**
*Table: `vehicle_types`*
| id (type_id) | type_name | hourly_rate |
| :--- | :--- | :--- |
| T1 | Car | 50.00 |

*Table: `parking_zones`*
| id (zone_id) | zone_name | description |
| :--- | :--- | :--- |
| Z1 | North Zone | Ground Floor |

*Table: `parking_spots`*
| spot_id | zone_id | type_id |
| :--- | :--- | :--- |
| S101 | Z1 | T1 |
| S102 | Z1 | T1 |

### 4. Boyce-Codd Normal Form (BCNF)
**Rule:** For every functional dependency $X \rightarrow Y$, $X$ must be a superkey.
**Action:** After 3NF, the dependency $zone\_id \rightarrow zone\_name$ acts via foreign key. Every LHS attribute in our dependencies across all 8 base tables uniquely identifies the relation (they are Primary Keys / Unique constants). E.g., `vehicle_plate` $\rightarrow$ `owner_name` in `monthly_passes` works uniquely because `vehicle_plate` is marked `UNIQUE` (a candidate key). Thus, the schema strictly adheres to BCNF.

**Demo Data Displaying Perfect BCNF:**
For every $X \rightarrow Y$, $X$ is a superkey. In `monthly_passes`, `vehicle_plate` determines the record, and `vehicle_plate` is a Unique Candidate Key.
*Table: `monthly_passes`*
| pass_id (PK) | vehicle_plate (UNIQUE) | owner_name |
| :--- | :--- | :--- |
| P001 | MH12AB1234 | Dipak Kumar |
| P002 | MH12CD5678 | Rahul Singh |

---

### 5. Fourth Normal Form (4NF)
**Rule:** It is in BCNF, and it contains no non-trivial **Multi-Valued Dependencies (MVDs)**.
**Problem Setup:** A customer can own multiple phone numbers AND multiple vehicles. 
If we put this in a combined table `customer_multi`, we see MVDs:
*   $customer\_id \twoheadrightarrow phone$
*   $customer\_id \twoheadrightarrow plate$
Because *phone* and *plate* are completely independent facts, combining them creates a cartesian product of redundancies.

**Before 4NF:**
*Table: `customer_multi`*
| customer_id | phone | plate |
| :--- | :--- | :--- |
| 1 | 9876543210 | MH12AB1234 |
| 1 | 9876543210 | MH12CD5678 |
| 1 | 8976543210 | MH12AB1234 |
| 1 | 8976543210 | MH12CD5678 |

**Decomposition (Lossless Join):** 
To eliminate cross-product repetitions, we isolated these independent sets ($\pi_{customer\_id, phone}$ and $\pi_{customer\_id, plate}$). *This proves 4NF by establishing standalone mappings!*

**After 4NF:**
*Table: `customer_phones`*
| customer_id | phone_number |
| :--- | :--- |
| 1 | 9876543210 |
| 1 | 8976543210 |

*Table: `customer_vehicles`*
| customer_id | vehicle_plate |
| :--- | :--- |
| 1 | MH12AB1234 |
| 1 | MH12CD5678 |

---

### 6. Fifth Normal Form (5NF / Project-Join Normal Form - PJNF)
**Rule:** Every join dependency is implied by the candidate keys.
**Problem Setup:** A ternary, cyclic relationship exists between `operator`, `zone`, and `shift`.
Suppose the business rule dictates: *If an operator is authorized for a zone, handles a specific shift type, and that zone needs coverage during that shift... then that operator is essentially "assigned" to that zone-shift.*

Sticking this in one table triggers a **Join Dependency** anomaly because the semantic relationships are actually binary, causing insert/delete failures if one tier is dropped.

**Before 5NF:**
*Table: `operator_assignments`*
| user_id | zone_id | shift_id |
| :--- | :--- | :--- |
| U1 | Z1 | SH1 |
| U1 | Z2 | SH1 |

**Decomposition & Relational Algebra Proof:**
We decompose into three 5NF irreducible binary projections ($\pi_{user, zone}$, $\pi_{user, shift}$, $\pi_{zone, shift}$). By breaking the cyclic ternary relationship into independent binary constraint tables, we successfully eliminated all insert/update bugs!

**After 5NF:**
*Table: `operator_zones`*
| user_id | zone_id |
| :--- | :--- |
| U1 | Z1 |
| U1 | Z2 |

*Table: `operator_shifts`*
| user_id | shift_id |
| :--- | :--- |
| U1 | SH1 |

*Table: `zone_shifts`*
| zone_id | shift_id |
| :--- | :--- |
| Z1 | SH1 |
| Z2 | SH1 |

---

---

## Before vs. After Schema Comparison

| Feature / State | Before Normalization (Unnormalized / 1NF Anomalies) | After Normalization (Up to 5NF) |
| :--- | :--- | :--- |
| **Table Structure** | Broad, multi-purpose, "flat" tables (e.g., `customer_details` mixing customer, vehicle, and shift data). | Granular, mathematically sound atomic tables (`customers`, `parking_zones`, `vehicle_types`). |
| **Data Redundancy** | Extremely High (Repeating customer names, zone names, and hourly rates across multiple rows). | Minimized/Eliminated (Each distinct fact is recorded in exactly one place). |
| **Multi-Valued Data** | Present (e.g., multiple `phones` combined as comma-separated text strings). | Resolved via 1NF/4NF (Separated into mapping tables like `customer_phones` and `customer_vehicles`). |
| **Partial Dependencies** | Present if composite primary keys were used alongside atomic attributes. | Eliminated in 2NF (All tables either have single-column PKs or fully dependent attributes). |
| **Transitive Dependencies**| Present (e.g., `spot_id` $\rightarrow$ `zone_id` $\rightarrow$ `zone_name`). | Removed in 3NF (Extracted into distinct tables like `parking_zones` and `vehicle_types`). |
| **Multi-Valued Dependencies**| Present (Cartesian product of independent sets, e.g., phones $\times$ plates). | Removed in 4NF (Decomposed into separate, independent mapping tables). |
| **Join Dependencies** | Cyclic ternary relations forcing artificial, hard-to-maintain combinations. | Removed in 5NF (Decomposed into irreducible binary projections like `operator_zones`). |
| **Anomalies** | Susceptible to major Insertion, Update, and Deletion anomalies, causing data corruption over time. | **Zero Anomalies.** Perfectly governed by FK restraints and relational algebra. |

---

## The "After" State
Through meticulous application of database constraints up to **Fifth Normal Form (5NF)**, the overarching schema is now represented correctly across atomic tables resulting in **Zero Anomalies**, maintaining **Lossless Join Property**, while ensuring mathematical **Dependency Preservation** via MySQL Foreign Keys configured with `ON DELETE CASCADE`.

The full SQL breakdown representing this is documented perfectly inside `advanced_dbms_schema.sql`.
