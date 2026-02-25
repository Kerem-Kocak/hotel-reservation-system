-- Hotel Reservation System - SQL Queries
-- =========================================
-- This file contains sample CRUD operations and useful reporting queries.

-- ============================================================
-- INSERT (CREATE)
-- ============================================================

-- Add a new guest
INSERT INTO guests (first_name, last_name, email, phone, address)
VALUES ('Alice', 'Johnson', 'alice.johnson@example.com', '+1-555-0101', '123 Maple St, Springfield');

-- Add a room type
INSERT INTO room_types (type_name, description, base_price, max_occupancy)
VALUES ('Deluxe Double', 'Spacious double room with city view', 150.00, 2);

-- Add a room
INSERT INTO rooms (room_number, floor, type_id, status)
VALUES ('201', 2, 1, 'available');

-- Create a reservation
INSERT INTO reservations (guest_id, check_in_date, check_out_date, status)
VALUES (1, '2026-03-10', '2026-03-15', 'confirmed');

-- Assign a room to a reservation (price snapshot)
INSERT INTO reservation_rooms (reservation_id, room_id, price_per_night)
VALUES (1, 1, 150.00);

-- Record a payment
INSERT INTO payments (reservation_id, amount, method, status)
VALUES (1, 750.00, 'credit_card', 'completed');


-- ============================================================
-- SELECT (READ)
-- ============================================================

-- List all available rooms with their type and nightly rate
SELECT r.room_number,
       r.floor,
       rt.type_name,
       rt.base_price
FROM   rooms r
JOIN   room_types rt ON r.type_id = rt.type_id
WHERE  r.status = 'available'
ORDER  BY r.room_number;

-- Get all reservations for a specific guest (by email)
SELECT res.reservation_id,
       res.check_in_date,
       res.check_out_date,
       res.status,
       DATEDIFF(res.check_out_date, res.check_in_date) AS nights
FROM   reservations res
JOIN   guests g ON res.guest_id = g.guest_id
WHERE  g.email = 'alice.johnson@example.com'
ORDER  BY res.check_in_date DESC;

-- Full reservation details with room and payment info
SELECT res.reservation_id,
       CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
       g.email,
       r.room_number,
       rt.type_name,
       res.check_in_date,
       res.check_out_date,
       DATEDIFF(res.check_out_date, res.check_in_date) AS nights,
       rr.price_per_night,
       DATEDIFF(res.check_out_date, res.check_in_date) * rr.price_per_night AS total_cost,
       p.amount           AS amount_paid,
       p.method           AS payment_method,
       p.status           AS payment_status
FROM   reservations res
JOIN   guests             g   ON res.guest_id        = g.guest_id
JOIN   reservation_rooms  rr  ON res.reservation_id  = rr.reservation_id
JOIN   rooms              r   ON rr.room_id           = r.room_id
JOIN   room_types         rt  ON r.type_id            = rt.type_id
LEFT JOIN payments        p   ON res.reservation_id  = p.reservation_id
ORDER  BY res.check_in_date;

-- Check room availability for a date range
SELECT r.room_id,
       r.room_number,
       rt.type_name,
       rt.base_price
FROM   rooms r
JOIN   room_types rt ON r.type_id = rt.type_id
WHERE  r.status = 'available'
  AND  r.room_id NOT IN (
           SELECT rr.room_id
           FROM   reservation_rooms rr
           JOIN   reservations res ON rr.reservation_id = res.reservation_id
           WHERE  res.status NOT IN ('cancelled', 'checked_out')
             AND  res.check_in_date  < '2026-03-15'
             AND  res.check_out_date > '2026-03-10'
       )
ORDER  BY r.room_number;

-- Monthly revenue report
SELECT DATE_FORMAT(p.payment_date, '%Y-%m') AS month,
       COUNT(p.payment_id)                  AS total_payments,
       SUM(p.amount)                        AS total_revenue
FROM   payments p
WHERE  p.status = 'completed'
GROUP  BY DATE_FORMAT(p.payment_date, '%Y-%m')
ORDER  BY month DESC;

-- Top 5 guests by total spending
SELECT CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
       g.email,
       COUNT(DISTINCT res.reservation_id)      AS total_reservations,
       SUM(p.amount)                           AS total_spent
FROM   guests g
JOIN   reservations res ON g.guest_id        = res.guest_id
JOIN   payments     p   ON res.reservation_id = p.reservation_id
WHERE  p.status = 'completed'
GROUP  BY g.guest_id
ORDER  BY total_spent DESC
LIMIT  5;

-- Occupancy rate by room type (for the current month)
SELECT rt.type_name,
       COUNT(DISTINCT r.room_id)                    AS total_rooms,
       COUNT(DISTINCT rr.room_id)                   AS occupied_rooms,
       ROUND(
           COUNT(DISTINCT rr.room_id) * 100.0
           / COUNT(DISTINCT r.room_id), 2)          AS occupancy_pct
FROM   room_types rt
JOIN   rooms r ON rt.type_id = r.type_id
LEFT JOIN reservation_rooms rr ON r.room_id = rr.room_id
LEFT JOIN reservations res     ON rr.reservation_id = res.reservation_id
    AND res.status NOT IN ('cancelled')
    AND MONTH(res.check_in_date) = MONTH(CURDATE())
    AND YEAR(res.check_in_date)  = YEAR(CURDATE())
GROUP  BY rt.type_id
ORDER  BY rt.type_name;


-- ============================================================
-- UPDATE
-- ============================================================

-- Confirm a pending reservation
UPDATE reservations
SET    status = 'confirmed'
WHERE  reservation_id = 1;

-- Mark a room as occupied when guest checks in
UPDATE rooms
SET    status = 'occupied'
WHERE  room_id = 1;

-- Mark a room as available after check-out
UPDATE rooms
SET    status = 'available'
WHERE  room_id = 1;

-- Update guest contact information
UPDATE guests
SET    phone   = '+1-555-0199',
       address = '456 Oak Ave, Springfield'
WHERE  email = 'alice.johnson@example.com';


-- ============================================================
-- DELETE
-- ============================================================

-- Cancel a reservation (soft-delete via status change is preferred)
UPDATE reservations
SET    status = 'cancelled'
WHERE  reservation_id = 1;

-- Hard-delete a guest (only if no reservations exist)
DELETE FROM guests
WHERE  guest_id = 1
  AND  guest_id NOT IN (SELECT guest_id FROM reservations);
