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
# COLUMN MIGRATION HELPER
# ============================================================

def ensure_column(
    connection,
    table_name,
    column_name,
    definition
):
    """
    Add a column if it does not already exist.

    This allows the project to evolve without deleting
    the existing SQLite database.
    """

    columns = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    existing_columns = {
        row["name"]
        for row in columns
    }

    if column_name not in existing_columns:

        connection.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {definition}
            """
        )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    """
    Initialize the OFFLINE COMM SYSTEM database.

    Existing data is preserved.

    New columns are added automatically when required.
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

                node_id TEXT,

                created_at TEXT NOT NULL

            )
            """
        )


        # ====================================================
        # USER MIGRATION
        # ====================================================

        ensure_column(
            connection,
            "users",
            "node_id",
            "TEXT"
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
        # MESSAGE MIGRATION
        # ====================================================

        ensure_column(
            connection,
            "messages",
            "node_id",
            "TEXT"
        )


        ensure_column(
            connection,
            "messages",
            "sender",
            "TEXT"
        )


        ensure_column(
            connection,
            "messages",
            "receiver",
            "TEXT"
        )


        ensure_column(
            connection,
            "messages",
            "message_type",
            "TEXT DEFAULT 'TEXT'"
        )


        ensure_column(
            connection,
            "messages",
            "status",
            "TEXT DEFAULT 'RECEIVED'"
        )


        ensure_column(
            connection,
            "messages",
            "created_at",
            "TEXT"
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


        # ====================================================
        # INDEXES
        # ====================================================

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_users_node_id
            ON users(node_id)
            """
        )


        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_conversation
            ON messages(sender, receiver, created_at)
            """
        )


        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_receiver
            ON messages(receiver, created_at)
            """
        )


        connection.commit()

    finally:

        connection.close()
