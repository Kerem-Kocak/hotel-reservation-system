"""
Configuration module for Hotel Reservation System.

Database credentials are loaded from a .env file.
Copy .env.template to .env and fill in your values.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "Hotel_Reservation_System"),
}
