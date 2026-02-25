"""
Database Manager for Hotel Reservation System.

All database interactions go through stored procedures and views.
No raw SQL queries are used in the application layer.
"""

import mysql.connector
from mysql.connector import Error

from config import DB_CONFIG


class DatabaseManager:
    """Manages MySQL database connections and stored procedure calls."""

    def __init__(self):
        self._connection = None

    # -- connection helpers ------------------------------------------------

    def connect(self):
        """Establish a database connection using config credentials."""
        if self._connection is None or not self._connection.is_connected():
            self._connection = mysql.connector.connect(**DB_CONFIG)
        return self._connection

    def disconnect(self):
        """Close the database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    # -- stored procedure wrappers ----------------------------------------

    def get_available_rooms(self, check_in_date, check_out_date):
        """Call sp_GetAvailableRooms and return the result set."""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_GetAvailableRooms", [check_in_date, check_out_date])
            for result in cursor.stored_results():
                return result.fetchall()
            return []
        finally:
            cursor.close()

    def get_guest_history(self, guest_id):
        """Call sp_GuestHistory and return the result set."""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_GuestHistory", [guest_id])
            for result in cursor.stored_results():
                return result.fetchall()
            return []
        finally:
            cursor.close()

    def create_reservation_with_payment(
        self,
        guest_id,
        room_id,
        booking_date,
        check_in_date,
        check_out_date,
        total_amount,
        payment_method,
    ):
        """Call sp_CreateResWithPay (transactional reservation + payment)."""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc(
                "sp_CreateResWithPay",
                [
                    guest_id,
                    room_id,
                    booking_date,
                    check_in_date,
                    check_out_date,
                    total_amount,
                    payment_method,
                ],
            )
            conn.commit()
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    return rows[0].get("ReservationID")
            return None
        finally:
            cursor.close()

    def get_room_type_performance(self):
        """Query the vw_RoomTypePerformance view via a stored procedure call."""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_RoomTypePerformance")
            for result in cursor.stored_results():
                return result.fetchall()
            return []
        finally:
            cursor.close()

    def get_all_guests(self):
        """Retrieve all guests via stored procedure."""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_GetAllGuests")
            for result in cursor.stored_results():
                return result.fetchall()
            return []
        finally:
            cursor.close()

    def get_confirmed_reservations(self):
        """Retrieve confirmed reservations via stored procedure."""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_GetConfirmedReservations")
            for result in cursor.stored_results():
                return result.fetchall()
            return []
        finally:
            cursor.close()

    def check_in_reservation(self, reservation_id):
        """Update reservation status to 'Checked-In'.

        This triggers trg_AutoUpdateRoomStatus in the database which
        automatically sets the room status to 'Occupied'.
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_CheckInReservation", [reservation_id])
            conn.commit()
        finally:
            cursor.close()
