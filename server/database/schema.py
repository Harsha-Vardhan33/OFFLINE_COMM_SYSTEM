"""
OFFLINE COMM SYSTEM
Database Schema Management
"""

from server.config import DATABASE_DIR
from server.database.connection import get_connection


# ============================================================
# DATABASE DIRECTORY
# ============================================================

def ensure_database_directory():
    """
    Ensure that the database directory exists.
    """

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    """
    Initialize the OFFLINE COMM SYSTEM database.

    Creates the required tables if they do not already exist.

    Existing tables are NOT deleted automatically.
    """

    ensure_database_directory()

    connection = get_connection()

    try:

        # ====================================================
        # USERS
        # ====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_name TEXT NOT NULL,

                created_at TEXT NOT NULL

            )
            """
        )


        # ====================================================
        # NODES
        # ====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS nodes (

                node_id TEXT PRIMARY KEY,

                node_name TEXT,

                ip_address TEXT,

                role TEXT DEFAULT 'NODE',

                status TEXT DEFAULT 'OFFLINE',

                battery REAL,

                signal_strength REAL,

                last_seen TEXT NOT NULL

            )
            """
        )


        # ====================================================
        # MESSAGES
        # ====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                node_id TEXT,

                sender TEXT,

                receiver TEXT,

                message TEXT NOT NULL,

                message_type TEXT DEFAULT 'TEXT',

                status TEXT DEFAULT 'RECEIVED',

                created_at TEXT NOT NULL

            )
            """
        )


        # ====================================================
        # LOCATIONS
        # ====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS locations (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                node_id TEXT,

                user_name TEXT,

                latitude REAL NOT NULL,

                longitude REAL NOT NULL,

                accuracy REAL,

                created_at TEXT NOT NULL

            )
            """
        )


        # ====================================================
        # SOS ALERTS
        # ====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sos_alerts (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                node_id TEXT,

                user_name TEXT,

                message TEXT,

                latitude REAL,

                longitude REAL,

                priority TEXT DEFAULT 'HIGH',

                status TEXT DEFAULT 'ACTIVE',

                created_at TEXT NOT NULL

            )
            """
        )


        # ====================================================
        # RESOURCE REQUESTS
        # ====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resource_requests (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                node_id TEXT,

                user_name TEXT,

                resource TEXT NOT NULL,

                quantity INTEGER DEFAULT 1,

                priority TEXT DEFAULT 'NORMAL',

                status TEXT DEFAULT 'PENDING',

                created_at TEXT NOT NULL

            )
            """
        )


        connection.commit()

    finally:

        connection.close()
