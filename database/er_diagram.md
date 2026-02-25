# Hotel Reservation System — ER Diagram

The entity-relationship diagram below is rendered with [Mermaid](https://mermaid.js.org/).
GitHub renders Mermaid diagrams natively in Markdown files.

```mermaid
erDiagram
    GUESTS {
        int     guest_id       PK
        varchar first_name
        varchar last_name
        varchar email          UK
        varchar phone
        varchar address
        datetime created_at
    }

    ROOM_TYPES {
        int     type_id        PK
        varchar type_name      UK
        varchar description
        decimal base_price
        int     max_occupancy
    }

    ROOMS {
        int     room_id        PK
        varchar room_number    UK
        int     floor
        int     type_id        FK
        enum    status
    }

    RESERVATIONS {
        int     reservation_id PK
        int     guest_id       FK
        date    check_in_date
        date    check_out_date
        enum    status
        datetime created_at
    }

    RESERVATION_ROOMS {
        int     reservation_room_id PK
        int     reservation_id      FK
        int     room_id             FK
        decimal price_per_night
    }

    PAYMENTS {
        int     payment_id     PK
        int     reservation_id FK
        decimal amount
        datetime payment_date
        enum    method
        enum    status
    }

    GUESTS         ||--o{ RESERVATIONS       : "makes"
    RESERVATIONS   ||--o{ RESERVATION_ROOMS  : "includes"
    ROOMS          ||--o{ RESERVATION_ROOMS  : "assigned to"
    ROOM_TYPES     ||--o{ ROOMS              : "categorises"
    RESERVATIONS   ||--o{ PAYMENTS           : "paid via"
```

## Relationship Summary

| Relationship | Cardinality | Description |
|---|---|---|
| GUESTS → RESERVATIONS | One-to-Many | A guest can have multiple reservations |
| RESERVATIONS → RESERVATION_ROOMS | One-to-Many | A reservation can cover multiple rooms |
| ROOMS → RESERVATION_ROOMS | One-to-Many | A room can appear in many reservations (at different times) |
| ROOM_TYPES → ROOMS | One-to-Many | A room type groups many rooms |
| RESERVATIONS → PAYMENTS | One-to-Many | A reservation can have multiple payment records (e.g. deposit + balance) |

## Normalisation Notes (3NF)

* **ROOM_TYPES** was extracted from **ROOMS** to eliminate the transitive dependency
  `room_id → type_name → base_price`.  Room-type attributes depend only on the type,
  not on the room number.
* **RESERVATION_ROOMS** (junction table) resolves the many-to-many relationship between
  **RESERVATIONS** and **ROOMS** and stores the price snapshot at booking time,
  avoiding update anomalies when base prices change later.
* All non-key attributes in every table depend solely on the primary key —
  satisfying First, Second, and Third Normal Form.
