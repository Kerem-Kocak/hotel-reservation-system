# Hotel Reservation System

A **3NF-normalised relational database** system designed to manage guests, room inventory, reservations and payments for a hotel.  The project includes:

* A full MySQL schema (`database/schema.sql`)
* Ready-to-run SQL queries for CRUD operations and reporting (`database/queries.sql`)
* An entity-relationship diagram (`database/er_diagram.md`)
* A Python data-access layer (`src/db.py`)

---

## Project Structure

```
hotel-reservation-system/
├── database/
│   ├── schema.sql      # DDL – table definitions (3NF)
│   ├── queries.sql     # DML – CRUD & reporting queries
│   └── er_diagram.md   # Mermaid ER diagram
├── src/
│   └── db.py           # Python DB connection & helper functions
└── README.md
```

---

## Database Design

### Tables

| Table | Description |
|---|---|
| `guests` | Hotel guests with contact details |
| `room_types` | Room categories (Single, Double, Suite, …) and their base nightly rate |
| `rooms` | Individual physical rooms linked to a type |
| `reservations` | Guest stay records with check-in / check-out dates and status |
| `reservation_rooms` | Junction table linking reservations to rooms (many-to-many) |
| `payments` | Payment records associated with reservations |

### Why 3NF?

* `room_types` was extracted from `rooms` to remove the transitive dependency `room_id → type_name → base_price`.
* `reservation_rooms` resolves the many-to-many relationship between reservations and rooms and stores a **price snapshot** at booking time, so later price changes do not affect historical records.
* Every non-key column in every table depends solely on its own primary key — satisfying 1NF, 2NF, and 3NF.

### ER Diagram

See [`database/er_diagram.md`](database/er_diagram.md) for the full Mermaid diagram.  A simplified overview:

```
GUESTS ──< RESERVATIONS ──< RESERVATION_ROOMS >── ROOMS >── ROOM_TYPES
                    └──< PAYMENTS
```

---

## Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| MySQL | 8.0+ |
| Python | 3.10+ |
| mysql-connector-python | 8.0+ |

### 1 — Create the database

```sql
CREATE DATABASE hotel_reservation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2 — Apply the schema

```bash
mysql -u root -p hotel_reservation < database/schema.sql
```

### 3 — (Optional) Load sample data

```bash
mysql -u root -p hotel_reservation < database/queries.sql
```

> The `queries.sql` file begins with several `INSERT` statements that populate the database with sample rows before showing the `SELECT` examples.

### 4 — Install the Python dependency

```bash
pip install mysql-connector-python
```

### 5 — Configure the connection

Set environment variables before running Python code (or edit `DB_CONFIG` in `src/db.py` directly):

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=hotel_reservation
export DB_USER=root
export DB_PASSWORD=your_password
```

### 6 — Run the smoke test

```bash
python src/db.py
```

Expected output:

```
Connecting to database …
Connected!  MySQL server version: 8.x.x
Available rooms:
  Room 201 (Deluxe Double) — $150.00/night
  …
```

---

## Python API Reference (`src/db.py`)

### Connection

```python
from src.db import get_connection

conn = get_connection()   # returns a MySQLConnection
conn.close()
```

### Guests

```python
guest_id = create_guest("Alice", "Johnson", "alice@example.com", phone="+1-555-0101")
guest    = get_guest_by_email("alice@example.com")   # → dict or None
guests   = list_guests()                              # → list[dict]
rows     = update_guest_contact(guest_id, phone="+1-555-0199")
```

### Rooms

```python
from datetime import date

rooms = list_available_rooms()                                          # all available
rooms = list_available_rooms(date(2026,3,10), date(2026,3,15))         # with date filter
rows  = update_room_status(room_id=1, status="maintenance")
```

### Reservations

```python
res_id = create_reservation(
    guest_id=1,
    check_in=date(2026, 3, 10),
    check_out=date(2026, 3, 15),
    room_ids=[1],
    price_per_night=150.00,
)
reservations = get_reservations_by_guest(guest_id=1)   # → list[dict]
cancel_reservation(reservation_id=res_id)
```

### Payments

```python
pay_id   = record_payment(res_id, amount=750.00, method="credit_card")
payments = get_payments_by_reservation(res_id)          # → list[dict]
```

---

## SQL Queries

`database/queries.sql` contains the following categories of queries:

* **INSERT** — add guests, room types, rooms, reservations, and payments
* **SELECT** — list available rooms, full reservation details, date-range availability check, monthly revenue report, top-spending guests, occupancy rate by room type
* **UPDATE** — confirm reservations, update room status, update guest contact info
* **DELETE** — soft-cancel reservations (status change), hard-delete guests with no history

---

## License

This project is released for educational purposes.
