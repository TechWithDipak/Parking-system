-- ==============================================================================
-- CAR PARKING MANAGEMENT SYSTEM - ADVANCED SQL QUERIES
-- ==============================================================================

USE parking_sys;

-- ==============================================================================
-- WEEK 4: Aggregate Functions, Constraints, and Set Operations
-- ==============================================================================

-- 1. Aggregate Functions: Calculate total revenue, average fee, and max fee collected
SELECT 
    COUNT(*) AS total_transactions,
    SUM(fee) AS total_revenue, 
    AVG(fee) AS average_fee,
    MAX(fee) AS highest_single_fee
FROM transactions 
WHERE exit_time IS NOT NULL;

-- 2. Aggregate Functions with GROUP BY: Total revenue per payment method
SELECT 
    payment_method, 
    SUM(amount) AS total_amount,
    COUNT(id) AS number_of_payments
FROM payments
GROUP BY payment_method;

-- 3. Constraints: Adding a CHECK constraint to ensure fees are never negative
-- (Note: MySQL enforces CHECK constraints starting from version 8.0.16)
ALTER TABLE transactions 
ADD CONSTRAINT chk_fee_positive CHECK (fee >= 0);

-- 4. Set Operations (UNION): Get a master list of all unique vehicle plates 
-- that have interacted with the system (both regular transactions and monthly passes)
SELECT vehicle_plate AS 'All_Vehicles' FROM transactions
UNION
SELECT vehicle_plate AS 'All_Vehicles' FROM monthly_passes;


-- ==============================================================================
-- WEEK 5: Subqueries, Joins, and Views
-- ==============================================================================

-- 5. Subqueries: Find transactions where the fee paid is higher than the overall average fee
SELECT 
    vehicle_plate, 
    entry_time, 
    exit_time, 
    fee 
FROM transactions 
WHERE fee > (
    SELECT AVG(fee) FROM transactions WHERE exit_time IS NOT NULL
);

-- 6. Joins (Multiple Tables): Generate a live snapshot of occupied spots, 
-- including zone details, vehicle types, and hourly rates.
SELECT 
    ps.spot_number, 
    pz.zone_name, 
    vt.type_name, 
    vt.hourly_rate,
    ps.vehicle_plate 
FROM parking_spots ps
INNER JOIN parking_zones pz ON ps.zone_id = pz.id
INNER JOIN vehicle_types vt ON ps.type_id = vt.id
WHERE ps.is_occupied = TRUE;

-- 7. Views: Create a reusable view for the dashboard to easily fetch active parking sessions
CREATE OR REPLACE VIEW active_parking_sessions AS
SELECT 
    t.id AS transaction_id, 
    t.vehicle_plate, 
    s.spot_number, 
    z.zone_name,
    t.entry_time
FROM transactions t
JOIN parking_spots s ON t.spot_id = s.spot_id
JOIN parking_zones z ON s.zone_id = z.id
WHERE t.exit_time IS NULL;

-- To query the view: 
-- SELECT * FROM active_parking_sessions;


-- ==============================================================================
-- WEEK 6: Functions, Triggers, Cursors, and Exception Handling
-- ==============================================================================

-- 8. Functions: Create a deterministic function to calculate parking duration in hours
DELIMITER //
CREATE FUNCTION CalculateParkingHours(entry_t DATETIME, exit_t DATETIME) 
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE duration_hours INT;
    -- Calculates difference in minutes and rounds up to the next full hour
    SET duration_hours = CEIL(TIMESTAMPDIFF(MINUTE, entry_t, exit_t) / 60);
    RETURN IFNULL(duration_hours, 0);
END //
DELIMITER ;

-- Test the function:
-- SELECT vehicle_plate, CalculateParkingHours(entry_time, exit_time) AS hours_parked FROM transactions WHERE exit_time IS NOT NULL;


-- 9. Triggers: Automatically free up a parking spot when a transaction is completed (exit_time updated)
DELIMITER //
CREATE TRIGGER after_transaction_update
AFTER UPDATE ON transactions
FOR EACH ROW
BEGIN
    -- If exit time just got filled in (checkout occurred)
    IF OLD.exit_time IS NULL AND NEW.exit_time IS NOT NULL THEN
        UPDATE parking_spots 
        SET is_occupied = FALSE, vehicle_plate = NULL 
        WHERE spot_id = NEW.spot_id;
    END IF;
END //
DELIMITER ;


-- 10. Cursors and Exception Handling: 
-- A Stored Procedure to iterate through all payments and calculate total cash collected.
-- It includes a custom CONTINUE HANDLER for exception handling.
DELIMITER //
CREATE PROCEDURE CalculateTotalCashRevenue()
BEGIN
    -- Variables for cursor and loops
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_amount DECIMAL(10,2);
    DECLARE total_cash DECIMAL(10,2) DEFAULT 0.00;
    
    -- Cursor Declaration (Selects only Cash payments)
    DECLARE payment_cursor CURSOR FOR 
        SELECT amount FROM payments WHERE payment_method = 'Cash';
        
    -- Exception Handling: Catch-all for SQL exceptions
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION 
    BEGIN
        SELECT 'An error occurred during processing.' AS ErrorMessage;
    END;

    -- Exception Handling: When cursor reaches the end of the rows
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Open the cursor
    OPEN payment_cursor;

    -- Loop through the rows
    read_loop: LOOP
        FETCH payment_cursor INTO v_amount;
        
        -- Exit loop if no more rows
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Accumulate the cash amount
        SET total_cash = total_cash + v_amount;
    END LOOP;

    -- Close cursor
    CLOSE payment_cursor;

    -- Output the result
    SELECT total_cash AS 'Total_Cash_Revenue_Calculated_Via_Cursor';
END //
DELIMITER ;

-- To execute the stored procedure:
-- CALL CalculateTotalCashRevenue();