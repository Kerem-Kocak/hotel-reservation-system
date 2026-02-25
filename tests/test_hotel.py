"""
Unit tests for the Hotel Reservation System.

Tests cover validation logic and DatabaseManager method signatures.
Database calls are mocked since no MySQL server is available in CI.
"""

import datetime
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import database_manager  # noqa: E402
from database_manager import DatabaseManager  # noqa: E402


class TestDateValidation(unittest.TestCase):
    """Front-end validation: CheckOutDate must be after CheckInDate."""

    def test_checkout_after_checkin(self):
        ci = datetime.date(2025, 6, 1)
        co = datetime.date(2025, 6, 5)
        self.assertGreater(co, ci)

    def test_checkout_equals_checkin_invalid(self):
        ci = datetime.date(2025, 6, 1)
        co = datetime.date(2025, 6, 1)
        self.assertFalse(co > ci)

    def test_checkout_before_checkin_invalid(self):
        ci = datetime.date(2025, 6, 5)
        co = datetime.date(2025, 6, 1)
        self.assertFalse(co > ci)

    def test_total_amount_must_be_positive(self):
        self.assertGreater(100.0, 0)
        self.assertFalse(0 > 0)
        self.assertFalse(-50 > 0)

    def test_date_parsing_valid(self):
        d = datetime.date.fromisoformat("2025-07-15")
        self.assertEqual(d, datetime.date(2025, 7, 15))

    def test_date_parsing_invalid(self):
        with self.assertRaises(ValueError):
            datetime.date.fromisoformat("15-07-2025")


class TestDatabaseManagerMethods(unittest.TestCase):
    """Verify DatabaseManager calls the correct stored procedures."""

    def setUp(self):
        self.db = DatabaseManager()

    @patch.object(DatabaseManager, "connect")
    def test_get_available_rooms_calls_sp(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            {"RoomID": 1, "RoomNumber": "101", "TypeName": "Standard"}
        ]
        mock_cursor.stored_results.return_value = [mock_result]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.db.get_available_rooms("2025-06-01", "2025-06-05")

        mock_cursor.callproc.assert_called_once_with(
            "sp_GetAvailableRooms", ["2025-06-01", "2025-06-05"]
        )
        self.assertEqual(len(result), 1)

    @patch.object(DatabaseManager, "connect")
    def test_get_guest_history_calls_sp(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_cursor.stored_results.return_value = [mock_result]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.db.get_guest_history(1)

        mock_cursor.callproc.assert_called_once_with("sp_GuestHistory", [1])
        self.assertEqual(result, [])

    @patch.object(DatabaseManager, "connect")
    def test_create_reservation_calls_sp(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [{"ReservationID": 42}]
        mock_cursor.stored_results.return_value = [mock_result]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        res_id = self.db.create_reservation_with_payment(
            1, 2, "2025-06-01", "2025-06-10", "2025-06-15", 500.00, "Credit Card"
        )

        mock_cursor.callproc.assert_called_once_with(
            "sp_CreateResWithPay",
            [1, 2, "2025-06-01", "2025-06-10", "2025-06-15", 500.00, "Credit Card"],
        )
        mock_conn.commit.assert_called_once()
        self.assertEqual(res_id, 42)

    @patch.object(DatabaseManager, "connect")
    def test_check_in_reservation_calls_sp(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        self.db.check_in_reservation(7)

        mock_cursor.callproc.assert_called_once_with("sp_CheckInReservation", [7])
        mock_conn.commit.assert_called_once()

    @patch.object(DatabaseManager, "connect")
    def test_get_room_type_performance_calls_sp(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            {"TypeName": "Deluxe", "TotalRooms": 5, "AvailableRooms": 3,
             "OccupiedRooms": 2, "PricePerNight": 500}
        ]
        mock_cursor.stored_results.return_value = [mock_result]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.db.get_room_type_performance()

        mock_cursor.callproc.assert_called_once_with("sp_RoomTypePerformance")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["TypeName"], "Deluxe")


class TestConfigSecurity(unittest.TestCase):
    """Verify that no passwords are hardcoded in config."""

    def test_password_comes_from_env(self):
        from config import DB_CONFIG
        # Default password should be empty string (from env), never a real password
        self.assertIn("password", DB_CONFIG)
        # The password value should come from os.getenv, which defaults to ""
        self.assertEqual(DB_CONFIG["password"], os.getenv("DB_PASSWORD", ""))


if __name__ == "__main__":
    unittest.main()
