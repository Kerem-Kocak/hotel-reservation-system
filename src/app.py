"""
Hotel Reservation System – Desktop Application.

Built with CustomTkinter for a modern look.  All database access goes through
DatabaseManager which only calls stored procedures.
"""

import datetime
from tkinter import messagebox

import customtkinter as ctk

from database_manager import DatabaseManager
import mysql.connector


# ── Appearance ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Colour palette ──────────────────────────────────────────────────────────
SIDEBAR_BG = "#1a1a2e"
CONTENT_BG = "#16213e"
ACCENT = "#0f3460"
HIGHLIGHT = "#e94560"


class HotelApp(ctk.CTk):
    """Main application window with sidebar navigation."""

    def __init__(self):
        super().__init__()
        self.title("Hotel Reservation System")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.db = DatabaseManager()

        # ── Layout ──────────────────────────────────────────────────────────
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # Start on Dashboard
        self.show_dashboard()

    # ── Sidebar ─────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=SIDEBAR_BG)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_rowconfigure(7, weight=1)

        logo = ctk.CTkLabel(
            sidebar,
            text="🏨 Hotel RS",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        logo.grid(row=0, column=0, padx=20, pady=(20, 30))

        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("🔍 Search Rooms", self.show_search_rooms),
            ("📝 New Booking", self.show_new_booking),
            ("👤 Guest History", self.show_guest_history),
            ("✅ Check-In", self.show_check_in),
        ]
        for idx, (text, command) in enumerate(buttons, start=1):
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                fg_color="transparent",
                hover_color=ACCENT,
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=14),
            )
            btn.grid(row=idx, column=0, padx=10, pady=4, sticky="ew")

    # ── Content area ────────────────────────────────────────────────────────

    def _build_content_area(self):
        self.content = ctk.CTkFrame(self, fg_color=CONTENT_BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nswe")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ── Pages ───────────────────────────────────────────────────────────────

    # 1. Dashboard ──────────────────────────────────────────────────────────

    def show_dashboard(self):
        self._clear_content()
        header = ctk.CTkLabel(
            self.content,
            text="Dashboard – Room Statistics",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        try:
            data = self.db.get_room_type_performance()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        if not data:
            ctk.CTkLabel(
                self.content,
                text="No room data available. Check your database connection.",
                font=ctk.CTkFont(size=14),
            ).grid(row=1, column=0, padx=20, pady=10, sticky="w")
            return

        cols = ("Type", "Total", "Available", "Occupied", "Price/Night")
        table_frame = ctk.CTkScrollableFrame(self.content, fg_color=ACCENT)
        table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nswe")
        self.content.grid_rowconfigure(1, weight=1)

        for c, col_name in enumerate(cols):
            ctk.CTkLabel(
                table_frame,
                text=col_name,
                font=ctk.CTkFont(size=13, weight="bold"),
                width=140,
            ).grid(row=0, column=c, padx=5, pady=5)

        for r, row in enumerate(data, start=1):
            vals = [
                row.get("TypeName", ""),
                row.get("TotalRooms", 0),
                row.get("AvailableRooms", 0),
                row.get("OccupiedRooms", 0),
                f"${row.get('PricePerNight', 0):,.2f}",
            ]
            for c, val in enumerate(vals):
                ctk.CTkLabel(table_frame, text=str(val), width=140).grid(
                    row=r, column=c, padx=5, pady=3
                )

    # 2. Search Available Rooms ──────────────────────────────────────────────

    def show_search_rooms(self):
        self._clear_content()
        header = ctk.CTkLabel(
            self.content,
            text="Search Available Rooms",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        header.grid(row=0, column=0, columnspan=4, padx=20, pady=(20, 10), sticky="w")

        ctk.CTkLabel(self.content, text="Check-In (YYYY-MM-DD):").grid(
            row=1, column=0, padx=20, pady=5, sticky="w"
        )
        entry_in = ctk.CTkEntry(self.content, width=160)
        entry_in.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.content, text="Check-Out (YYYY-MM-DD):").grid(
            row=1, column=2, padx=20, pady=5, sticky="w"
        )
        entry_out = ctk.CTkEntry(self.content, width=160)
        entry_out.grid(row=1, column=3, padx=5, pady=5)

        result_frame = ctk.CTkScrollableFrame(self.content, fg_color=ACCENT)
        result_frame.grid(row=3, column=0, columnspan=4, padx=20, pady=10, sticky="nswe")
        self.content.grid_rowconfigure(3, weight=1)

        def _search():
            # Validate
            try:
                ci = datetime.date.fromisoformat(entry_in.get().strip())
                co = datetime.date.fromisoformat(entry_out.get().strip())
            except ValueError:
                messagebox.showwarning("Validation", "Enter dates in YYYY-MM-DD format.")
                return
            if co <= ci:
                messagebox.showwarning(
                    "Validation", "Check-Out date must be after Check-In date."
                )
                return

            for w in result_frame.winfo_children():
                w.destroy()

            try:
                rooms = self.db.get_available_rooms(ci, co)
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))
                return

            cols = ("Room #", "Floor", "Type", "Capacity", "Price/Night")
            for c, col_name in enumerate(cols):
                ctk.CTkLabel(
                    result_frame,
                    text=col_name,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    width=120,
                ).grid(row=0, column=c, padx=5, pady=5)

            if not rooms:
                ctk.CTkLabel(result_frame, text="No rooms available for these dates.").grid(
                    row=1, column=0, columnspan=5, pady=10
                )
                return

            for r, room in enumerate(rooms, start=1):
                vals = [
                    room.get("RoomNumber", ""),
                    room.get("Floor", ""),
                    room.get("TypeName", ""),
                    room.get("Capacity", ""),
                    f"${room.get('PricePerNight', 0):,.2f}",
                ]
                for c, val in enumerate(vals):
                    ctk.CTkLabel(result_frame, text=str(val), width=120).grid(
                        row=r, column=c, padx=5, pady=3
                    )

        ctk.CTkButton(self.content, text="Search", command=_search, fg_color=HIGHLIGHT).grid(
            row=2, column=0, columnspan=4, padx=20, pady=5
        )

    # 3. New Booking ────────────────────────────────────────────────────────

    def show_new_booking(self):
        self._clear_content()
        header = ctk.CTkLabel(
            self.content,
            text="New Booking",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        header.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        labels = [
            "Guest ID:",
            "Room ID:",
            "Check-In (YYYY-MM-DD):",
            "Check-Out (YYYY-MM-DD):",
            "Total Amount:",
            "Payment Method:",
        ]
        entries = {}
        for i, lbl in enumerate(labels, start=1):
            ctk.CTkLabel(self.content, text=lbl).grid(
                row=i, column=0, padx=20, pady=5, sticky="w"
            )
            if lbl == "Payment Method:":
                combo = ctk.CTkComboBox(
                    self.content,
                    values=["Credit Card", "Cash", "Bank Transfer"],
                    width=200,
                )
                combo.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entries[lbl] = combo
            else:
                ent = ctk.CTkEntry(self.content, width=200)
                ent.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                entries[lbl] = ent

        def _book():
            try:
                guest_id = int(entries["Guest ID:"].get().strip())
                room_id = int(entries["Room ID:"].get().strip())
                ci = datetime.date.fromisoformat(
                    entries["Check-In (YYYY-MM-DD):"].get().strip()
                )
                co = datetime.date.fromisoformat(
                    entries["Check-Out (YYYY-MM-DD):"].get().strip()
                )
                amount = float(entries["Total Amount:"].get().strip())
                method = entries["Payment Method:"].get().strip()
            except (ValueError, AttributeError):
                messagebox.showwarning("Validation", "Please fill all fields correctly.")
                return

            if co <= ci:
                messagebox.showwarning(
                    "Validation", "Check-Out date must be after Check-In date."
                )
                return
            if amount <= 0:
                messagebox.showwarning("Validation", "Total amount must be greater than 0.")
                return

            booking_date = datetime.date.today()
            if ci < booking_date:
                messagebox.showwarning(
                    "Validation", "Check-In date cannot be in the past."
                )
                return

            try:
                res_id = self.db.create_reservation_with_payment(
                    guest_id, room_id, booking_date, ci, co, amount, method
                )
                messagebox.showinfo(
                    "Success", f"Reservation created!  ID: {res_id}"
                )
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))

        ctk.CTkButton(
            self.content, text="Book Now", command=_book, fg_color=HIGHLIGHT
        ).grid(row=len(labels) + 1, column=0, columnspan=2, padx=20, pady=15)

    # 4. Guest History ──────────────────────────────────────────────────────

    def show_guest_history(self):
        self._clear_content()
        header = ctk.CTkLabel(
            self.content,
            text="Guest History",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        header.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")

        ctk.CTkLabel(self.content, text="Guest ID:").grid(
            row=1, column=0, padx=20, pady=5, sticky="w"
        )
        entry_gid = ctk.CTkEntry(self.content, width=120)
        entry_gid.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        result_frame = ctk.CTkScrollableFrame(self.content, fg_color=ACCENT)
        result_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky="nswe")
        self.content.grid_rowconfigure(3, weight=1)

        def _lookup():
            try:
                gid = int(entry_gid.get().strip())
            except ValueError:
                messagebox.showwarning("Validation", "Enter a valid Guest ID.")
                return

            for w in result_frame.winfo_children():
                w.destroy()

            try:
                history = self.db.get_guest_history(gid)
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))
                return

            cols = (
                "Res. ID",
                "Room",
                "Type",
                "Check-In",
                "Check-Out",
                "Amount",
                "Status",
                "Pay Method",
                "Pay Status",
            )
            for c, col_name in enumerate(cols):
                ctk.CTkLabel(
                    result_frame,
                    text=col_name,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=100,
                ).grid(row=0, column=c, padx=4, pady=5)

            if not history:
                ctk.CTkLabel(result_frame, text="No history found for this guest.").grid(
                    row=1, column=0, columnspan=len(cols), pady=10
                )
                return

            for r, rec in enumerate(history, start=1):
                vals = [
                    rec.get("ReservationID", ""),
                    rec.get("RoomNumber", ""),
                    rec.get("TypeName", ""),
                    rec.get("CheckInDate", ""),
                    rec.get("CheckOutDate", ""),
                    f"${rec.get('TotalAmount', 0):,.2f}",
                    rec.get("ReservationStatus", ""),
                    rec.get("PaymentMethod", ""),
                    rec.get("PaymentStatus", ""),
                ]
                for c, val in enumerate(vals):
                    ctk.CTkLabel(result_frame, text=str(val), width=100).grid(
                        row=r, column=c, padx=4, pady=2
                    )

        ctk.CTkButton(
            self.content, text="Look Up", command=_lookup, fg_color=HIGHLIGHT
        ).grid(row=2, column=0, columnspan=3, padx=20, pady=5)

    # 5. Check-In ───────────────────────────────────────────────────────────

    def show_check_in(self):
        self._clear_content()
        header = ctk.CTkLabel(
            self.content,
            text="Check-In – Confirmed Reservations",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        table_frame = ctk.CTkScrollableFrame(self.content, fg_color=ACCENT)
        table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nswe")
        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        def _refresh():
            for w in table_frame.winfo_children():
                w.destroy()

            try:
                reservations = self.db.get_confirmed_reservations()
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))
                return

            cols = ("Res. ID", "Guest", "Room", "Check-In", "Check-Out", "Status", "")
            for c, col_name in enumerate(cols):
                ctk.CTkLabel(
                    table_frame,
                    text=col_name,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    width=120,
                ).grid(row=0, column=c, padx=5, pady=5)

            if not reservations:
                ctk.CTkLabel(
                    table_frame, text="No confirmed reservations to check in."
                ).grid(row=1, column=0, columnspan=len(cols), pady=10)
                return

            for r, res in enumerate(reservations, start=1):
                vals = [
                    res.get("ReservationID", ""),
                    f"{res.get('FirstName', '')} {res.get('LastName', '')}",
                    res.get("RoomNumber", ""),
                    res.get("CheckInDate", ""),
                    res.get("CheckOutDate", ""),
                    res.get("ReservationStatus", ""),
                ]
                for c, val in enumerate(vals):
                    ctk.CTkLabel(table_frame, text=str(val), width=120).grid(
                        row=r, column=c, padx=5, pady=3
                    )

                rid = res.get("ReservationID")
                ctk.CTkButton(
                    table_frame,
                    text="Check In",
                    width=90,
                    fg_color=HIGHLIGHT,
                    command=lambda _rid=rid: _do_checkin(_rid),
                ).grid(row=r, column=len(vals), padx=5, pady=3)

        def _do_checkin(reservation_id):
            if not messagebox.askyesno(
                "Confirm", f"Check in reservation #{reservation_id}?"
            ):
                return
            try:
                self.db.check_in_reservation(reservation_id)
                messagebox.showinfo(
                    "Success",
                    f"Reservation #{reservation_id} checked in.\n"
                    "Room status updated to 'Occupied'.",
                )
                _refresh()
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e))

        _refresh()

    # ── Cleanup ─────────────────────────────────────────────────────────────

    def on_closing(self):
        self.db.disconnect()
        self.destroy()


def main():
    app = HotelApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
