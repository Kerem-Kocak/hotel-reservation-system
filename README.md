Project Architecture: Software & 3D AI Bridge
This system is built with a focus on data integrity through Third Normal Form (3NF) normalization. Beyond standard CRUD operations, it utilizes Stored Procedures for complex availability logic and Triggers for real-time room status updates.

## Python Desktop Application

A professional CustomTkinter interface following the MVC / Modular pattern.

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure database credentials
cp .env.template .env
# Edit .env with your MySQL credentials

# 3. Run the SQL script to create the database, tables, views,
#    stored procedures and triggers
mysql -u root -p < Hotel_Reservation_System.sql

# 4. Launch the application
cd src
python app.py
```

### Architecture

| File | Role |
|---|---|
| `src/config.py` | Loads DB credentials from `.env` (no hardcoded passwords) |
| `src/database_manager.py` | All DB access via stored procedures only |
| `src/app.py` | CustomTkinter UI with sidebar navigation |

### Features

- **Dashboard** – Room statistics from `vw_RoomTypePerformance` view
- **Search Rooms** – Calls `sp_GetAvailableRooms` with date validation
- **New Booking** – Calls `sp_CreateResWithPay` (transactional reservation + payment)
- **Guest History** – Calls `sp_GuestHistory`
- **Check-In** – Updates status to `Checked-In`, triggering `trg_AutoUpdateRoomStatus`
