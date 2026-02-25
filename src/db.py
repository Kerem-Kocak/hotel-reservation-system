"""
Hotel Reservation System — Database Access Layer
=================================================
Provides a thin wrapper around MySQL Connector/Python for common
CRUD operations on the hotel reservation database.

Requirements
------------
    pip install mysql-connector-python

Configuration
-------------
Set the following environment variables (or edit DB_CONFIG below):

    DB_HOST     – MySQL host          (default: localhost)
    DB_PORT     – MySQL port          (default: 3306)
    DB_NAME     – Database name       (default: hotel_reservation)
    DB_USER     – MySQL user          (default: root)
    DB_PASSWORD – MySQL password      (default: empty string)
"""

import os
from datetime import date
from typing import Optional

import mysql.connector
from mysql.connector import Error, MySQLConnection
from mysql.connector.cursor import MySQLCursorDict

# ---------------------------------------------------------------------------
# Connection configuration — override with environment variables
# ---------------------------------------------------------------------------
DB_CONFIG: dict = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "database": os.getenv("DB_NAME",     "hotel_reservation"),
    "user":     os.getenv("DB_USER",     "root"),
    "password": os.getenv("DB_PASSWORD", ""),
}


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def get_connection() -> MySQLConnection:
    """Return an open MySQL connection using DB_CONFIG."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as exc:
        raise ConnectionError(f"Could not connect to MySQL: {exc}") from exc


# ---------------------------------------------------------------------------
# Guest operations
# ---------------------------------------------------------------------------

def create_guest(
    first_name: str,
    last_name: str,
    email: str,
    phone: Optional[str] = None,
    address: Optional[str] = None,
) -> int:
    """Insert a new guest and return the generated guest_id."""
    sql = """
        INSERT INTO guests (first_name, last_name, email, phone, address)
        VALUES (%s, %s, %s, %s, %s)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (first_name, last_name, email, phone, address))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_guest_by_email(email: str) -> Optional[dict]:
    """Return a guest row as a dict, or None if not found."""
    sql = "SELECT * FROM guests WHERE email = %s"
    conn = get_connection()
    try:
        cursor: MySQLCursorDict = conn.cursor(dictionary=True)
        cursor.execute(sql, (email,))
        return cursor.fetchone()
    finally:
        conn.close()


def list_guests() -> list[dict]:
    """Return all guest rows."""
    conn = get_connection()
    try:
        cursor: MySQLCursorDict = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM guests ORDER BY last_name, first_name")
        return cursor.fetchall()
    finally:
        conn.close()


def update_guest_contact(
    guest_id: int,
    phone: Optional[str] = None,
    address: Optional[str] = None,
) -> int:
    """Update phone and/or address for a guest. Returns rows affected."""
    if phone is None and address is None:
        return 0
    updates, params = [], []
    if phone is not None:
        updates.append("phone = %s")
        params.append(phone)
    if address is not None:
        updates.append("address = %s")
        params.append(address)
    params.append(guest_id)
    sql = f"UPDATE guests SET {', '.join(updates)} WHERE guest_id = %s"
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            conn.commit()
            return cursor.rowcount
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Room operations
# ---------------------------------------------------------------------------

def list_available_rooms(
    check_in: Optional[date] = None,
    check_out: Optional[date] = None,
) -> list[dict]:
    """
    Return rooms that are available.
    If check_in and check_out are provided, also exclude rooms already booked
    for that date range.
    """
    base_sql = """
        SELECT r.room_id, r.room_number, r.floor,
               rt.type_name, rt.base_price, rt.max_occupancy
        FROM   rooms r
        JOIN   room_types rt ON r.type_id = rt.type_id
        WHERE  r.status = 'available'
    """
    params: list = []

    if check_in and check_out:
        base_sql += """
          AND r.room_id NOT IN (
                SELECT rr.room_id
                FROM   reservation_rooms rr
                JOIN   reservations res ON rr.reservation_id = res.reservation_id
                WHERE  res.status NOT IN ('cancelled', 'checked_out')
                  AND  res.check_in_date  < %s
                  AND  res.check_out_date > %s
          )
        """
        params = [check_out, check_in]

    base_sql += " ORDER BY r.room_number"
    conn = get_connection()
    try:
        cursor: MySQLCursorDict = conn.cursor(dictionary=True)
        cursor.execute(base_sql, params)
        return cursor.fetchall()
    finally:
        conn.close()


def update_room_status(room_id: int, status: str) -> int:
    """Set the status of a room. Returns rows affected."""
    allowed = {"available", "occupied", "maintenance"}
    if status not in allowed:
        raise ValueError(f"status must be one of {allowed}")
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE rooms SET status = %s WHERE room_id = %s",
                (status, room_id),
            )
            conn.commit()
            return cursor.rowcount
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Reservation operations
# ---------------------------------------------------------------------------

def create_reservation(
    guest_id: int,
    check_in: date,
    check_out: date,
    room_ids: list[int],
    price_per_night: float,
    status: str = "confirmed",
) -> int:
    """
    Create a reservation for *guest_id*, assign *room_ids* to it, and mark
    those rooms as occupied.  Returns the new reservation_id.
    """
    if check_out <= check_in:
        raise ValueError("check_out must be after check_in")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Insert reservation
            cursor.execute(
                """
                INSERT INTO reservations (guest_id, check_in_date, check_out_date, status)
                VALUES (%s, %s, %s, %s)
                """,
                (guest_id, check_in, check_out, status),
            )
            reservation_id = cursor.lastrowid

            # Link rooms
            for room_id in room_ids:
                cursor.execute(
                    """
                    INSERT INTO reservation_rooms (reservation_id, room_id, price_per_night)
                    VALUES (%s, %s, %s)
                    """,
                    (reservation_id, room_id, price_per_night),
                )
                cursor.execute(
                    "UPDATE rooms SET status = 'occupied' WHERE room_id = %s",
                    (room_id,),
                )

            conn.commit()
            return reservation_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_reservations_by_guest(guest_id: int) -> list[dict]:
    """Return all reservations for a guest, newest first."""
    sql = """
        SELECT res.reservation_id,
               res.check_in_date,
               res.check_out_date,
               res.status,
               DATEDIFF(res.check_out_date, res.check_in_date) AS nights
        FROM   reservations res
        WHERE  res.guest_id = %s
        ORDER  BY res.check_in_date DESC
    """
    conn = get_connection()
    try:
        cursor: MySQLCursorDict = conn.cursor(dictionary=True)
        cursor.execute(sql, (guest_id,))
        return cursor.fetchall()
    finally:
        conn.close()


def cancel_reservation(reservation_id: int) -> int:
    """Cancel a reservation and free its rooms. Returns rows affected."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Free the rooms
            cursor.execute(
                """
                UPDATE rooms r
                JOIN   reservation_rooms rr ON r.room_id = rr.room_id
                SET    r.status = 'available'
                WHERE  rr.reservation_id = %s
                """,
                (reservation_id,),
            )
            # Cancel the reservation
            cursor.execute(
                "UPDATE reservations SET status = 'cancelled' WHERE reservation_id = %s",
                (reservation_id,),
            )
            conn.commit()
            return cursor.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Payment operations
# ---------------------------------------------------------------------------

def record_payment(
    reservation_id: int,
    amount: float,
    method: str,
    status: str = "completed",
) -> int:
    """Insert a payment record and return the new payment_id."""
    allowed_methods = {"cash", "credit_card", "debit_card", "bank_transfer", "online"}
    if method not in allowed_methods:
        raise ValueError(f"method must be one of {allowed_methods}")
    sql = """
        INSERT INTO payments (reservation_id, amount, method, status)
        VALUES (%s, %s, %s, %s)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (reservation_id, amount, method, status))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_payments_by_reservation(reservation_id: int) -> list[dict]:
    """Return all payment rows for a given reservation."""
    conn = get_connection()
    try:
        cursor: MySQLCursorDict = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM payments WHERE reservation_id = %s ORDER BY payment_date",
            (reservation_id,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Quick demo / smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Connecting to database …")
    conn = get_connection()
    print(f"Connected!  MySQL server version: {conn.get_server_info()}")
    conn.close()

    print("\nAvailable rooms:")
    for room in list_available_rooms():
        print(f"  Room {room['room_number']} ({room['type_name']}) — "
              f"${room['base_price']:.2f}/night")
