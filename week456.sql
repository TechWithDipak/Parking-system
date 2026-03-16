USE parking_sys;

-- WEEK 4: Aggregate Functions, Constraints, and Set Operations

SELECT 
    COUNT(*) AS total_transactions,
    SUM(fee) AS total_revenue, 
    AVG(fee) AS average_fee,
    MAX(fee) AS highest_single_fee
FROM transactions 
WHERE exit_time IS NOT NULL;

SELECT 
    payment_method, 
    SUM(amount) AS total_amount,
    COUNT(id) AS number_of_payments
FROM payments
GROUP BY payment_method;

ALTER TABLE transactions 
ADD CONSTRAINT chk_fee_positive CHECK (fee >= 0);

SELECT vehicle_plate AS 'All_Vehicles' FROM transactions
UNION
SELECT vehicle_plate AS 'All_Vehicles' FROM monthly_passes;


-- WEEK 5: Subqueries, Joins, and Views

SELECT 
    vehicle_plate, 
    entry_time, 
    exit_time, 
    fee 
FROM transactions 
WHERE fee > (
    SELECT AVG(fee) FROM transactions WHERE exit_time IS NOT NULL
);

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


-- WEEK 6: Functions, Triggers, Cursors, and Exception Handling

DROP FUNCTION IF EXISTS CalculateParkingHours;

DELIMITER //
CREATE FUNCTION CalculateParkingHours(entry_t DATETIME, exit_t DATETIME) 
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE duration_hours INT;
    SET duration_hours = CEIL(TIMESTAMPDIFF(MINUTE, entry_t, exit_t) / 60);
    RETURN IFNULL(duration_hours, 0);
END //
DELIMITER ;

DROP TRIGGER IF EXISTS after_transaction_update;

DELIMITER //
CREATE TRIGGER after_transaction_update
AFTER UPDATE ON transactions
FOR EACH ROW
BEGIN
    IF OLD.exit_time IS NULL AND NEW.exit_time IS NOT NULL THEN
        UPDATE parking_spots 
        SET is_occupied = FALSE, vehicle_plate = NULL 
        WHERE spot_id = NEW.spot_id;
    END IF;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS CalculateTotalCashRevenue;

DELIMITER //
CREATE PROCEDURE CalculateTotalCashRevenue()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_amount DECIMAL(10,2);
    DECLARE total_cash DECIMAL(10,2) DEFAULT 0.00;
    
    DECLARE payment_cursor CURSOR FOR 
        SELECT amount FROM payments WHERE payment_method = 'Cash';
        
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION 
    BEGIN
        SELECT 'An error occurred during processing.' AS ErrorMessage;
    END;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN payment_cursor;

    read_loop: LOOP
        FETCH payment_cursor INTO v_amount;
        
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        SET total_cash = total_cash + v_amount;
    END LOOP;

    CLOSE payment_cursor;

    SELECT total_cash AS 'Total_Cash_Revenue_Calculated_Via_Cursor';
END //
DELIMITER ;