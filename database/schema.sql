-- Hotel Reservation System - Database Schema (3NF Normalized)
-- ============================================================

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS reservation_rooms;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS room_types;
DROP TABLE IF EXISTS guests;

-- ---------------------------------------------------------------
-- Table: guests
-- Stores information about hotel guests.
-- ---------------------------------------------------------------
CREATE TABLE guests (
    guest_id    INT           NOT NULL AUTO_INCREMENT,
    first_name  VARCHAR(50)   NOT NULL,
    last_name   VARCHAR(50)   NOT NULL,
    email       VARCHAR(100)  NOT NULL UNIQUE,
    phone       VARCHAR(20),
    address     VARCHAR(200),
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (guest_id)
);

-- ---------------------------------------------------------------
-- Table: room_types
-- Stores room category information (e.g. Single, Double, Suite).
-- Separating this avoids repeating room-type details in every room row (3NF).
-- ---------------------------------------------------------------
CREATE TABLE room_types (
    type_id         INT           NOT NULL AUTO_INCREMENT,
    type_name       VARCHAR(50)   NOT NULL UNIQUE,   -- e.g. 'Single', 'Double', 'Suite'
    description     VARCHAR(255),
    base_price      DECIMAL(10,2) NOT NULL,          -- nightly rate
    max_occupancy   INT           NOT NULL DEFAULT 2,
    PRIMARY KEY (type_id)
);

-- ---------------------------------------------------------------
-- Table: rooms
-- Stores individual hotel rooms.
-- ---------------------------------------------------------------
CREATE TABLE rooms (
    room_id     INT           NOT NULL AUTO_INCREMENT,
    room_number VARCHAR(10)   NOT NULL UNIQUE,
    floor       INT           NOT NULL,
    type_id     INT           NOT NULL,
    status      ENUM('available', 'occupied', 'maintenance') NOT NULL DEFAULT 'available',
    PRIMARY KEY (room_id),
    FOREIGN KEY (type_id) REFERENCES room_types (type_id)
);

-- ---------------------------------------------------------------
-- Table: reservations
-- Stores one reservation per guest stay.
-- ---------------------------------------------------------------
CREATE TABLE reservations (
    reservation_id  INT           NOT NULL AUTO_INCREMENT,
    guest_id        INT           NOT NULL,
    check_in_date   DATE          NOT NULL,
    check_out_date  DATE          NOT NULL,
    status          ENUM('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled')
                                  NOT NULL DEFAULT 'pending',
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reservation_id),
    FOREIGN KEY (guest_id) REFERENCES guests (guest_id),
    CONSTRAINT chk_dates CHECK (check_out_date > check_in_date)
);

-- ---------------------------------------------------------------
-- Table: reservation_rooms
-- Junction table linking reservations to rooms (many-to-many).
-- A reservation may cover multiple rooms; a room may appear in
-- multiple reservations at different times.
-- ---------------------------------------------------------------
CREATE TABLE reservation_rooms (
    reservation_room_id INT           NOT NULL AUTO_INCREMENT,
    reservation_id      INT           NOT NULL,
    room_id             INT           NOT NULL,
    price_per_night     DECIMAL(10,2) NOT NULL,   -- snapshot of price at booking time
    PRIMARY KEY (reservation_room_id),
    UNIQUE KEY uq_res_room (reservation_id, room_id),
    FOREIGN KEY (reservation_id) REFERENCES reservations (reservation_id),
    FOREIGN KEY (room_id)        REFERENCES rooms (room_id)
);

-- ---------------------------------------------------------------
-- Table: payments
-- Stores payment records associated with reservations.
-- ---------------------------------------------------------------
CREATE TABLE payments (
    payment_id      INT             NOT NULL AUTO_INCREMENT,
    reservation_id  INT             NOT NULL,
    amount          DECIMAL(10,2)   NOT NULL,
    payment_date    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    method          ENUM('cash', 'credit_card', 'debit_card', 'bank_transfer', 'online')
                                    NOT NULL,
    status          ENUM('pending', 'completed', 'refunded', 'failed')
                                    NOT NULL DEFAULT 'pending',
    PRIMARY KEY (payment_id),
    FOREIGN KEY (reservation_id) REFERENCES reservations (reservation_id)
);
