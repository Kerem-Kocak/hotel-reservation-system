# Hotel Reservation System Database

This repository contains the complete SQL database schema, stored procedures, functions, and triggers for a **Hotel or Accommodation Reservation System**
It is designed to manage guests, room inventory, and financial transactions with high data integrity.

## 🏨 Project Overview
The system handles daily hotel operations, allowing staff to manage bookings and guests to browse room availability. 

### Key Features
**Guest Management**: Stores personal details including a unique National ID for legal compliance.</p>
**Room Inventory**: Categorizes rooms by type (e.g., "Deluxe Suite") with real-time status tracking.</p>
**Automated Logic**: Prevents double-booking and automatically updates room statuses upon check-in/out.</p>
**Financial Reporting**: Tracks multiple payments per reservation and calculates yearly revenue.

---

## 📊 Database Schema
The database is normalized to **Third Normal Form (3NF)** to minimize redundancy.



### Core Tables
**`Guests`**: Stores names, unique emails, and identification.</p>
**`RoomTypes`**: Defines category-based pricing and capacity.</p>
**`Rooms`**: Tracks physical room numbers, floors, and current status.</p>
**`Reservations`**: Links guests to rooms for specific dates.</p>
**`Payments`**: Records transaction history and payment methods.

---

## 🛠️ SQL Implementation

### Stored Procedures
**`sp_GetAvailableRooms`**: Checks availability for a specific date range using a `NOT IN` subquery.</p>
**`sp_GuestHistory`**: Retrieves a full history of a guest's bookings ordered by date[cite: 217, 224].</p>
**`sp_CreateResWithPay`**: Uses **Transactions** to ensure a reservation and its deposit are created atomically.

### Functions & Triggers
**`fn_CalculateYearlyRevenue`**: Sums all 'Completed' payments for a specific year.</p>
**`fn_CountAvailableRooms`**: Returns the count of available rooms for a specific category.</p>
**`trg_AutoUpdateRoomStatus`**: An `AFTER UPDATE` trigger that changes room status to 'Occupied' or 'Available' based on the reservation status.

---

## ⚖️ Business Constraints
**Date Logic**: `CheckOutDate` must always be later than `CheckInDate`.</p>
**Financial Protection**: Reservations with associated payments cannot be deleted (`On Delete Restrict`).</p>
**Double-Booking**: Prevented via logic checks in triggers or stored procedures.

## 🚀 How to Use
1. Execute the `Hotel_Reservation_System.sql` file in your MySQL environment.</p>
2. Use the following command to check room availability:
   ```sql
   CALL sp_GetAvailableRooms('2026-01-01', '2026-01-05');
