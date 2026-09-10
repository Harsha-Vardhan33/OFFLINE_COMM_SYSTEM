"""
OFFLINE COMM SYSTEM
Development Database Reset

Purpose:
    Reset the development database to a clean messaging state.

The reset:
    - Creates a timestamped backup.
    - Clears old test communication data.
    - Clears old test users.
    - Creates two clean development users.
    - Preserves the existing database schema.

Canonical database:
    server/database/offline_comm.db
"""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT
    / "server"
    / "database"
    / "offline_comm.db"
)

BACKUP_DIRECTORY = PROJECT_ROOT / "backups"


# ============================================================
# DEVELOPMENT USERS
# ============================================================

DEVELOPMENT_USERS = [
    {
        "user_name": "Harsha",
        "node_id": "PHONE_001",
    },
    {
        "user_name": "Alice",
        "node_id": "PHONE_002",
    },
]


# ============================================================
# TIME
# ============================================================

def current_timestamp() -> str:
    """
    Return an ISO-style local timestamp.
    """

    return datetime.now().isoformat()


# ============================================================
# BACKUP
# ============================================================

def create_backup() -> Path:
    """
    Create a timestamped backup before modifying the database.
    """

    BACKUP_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = (
        BACKUP_DIRECTORY
        / f"offline_comm_before_reset_{timestamp}.db"
    )

    shutil.copy2(
        DATABASE_PATH,
        backup_path,
    )

    return backup_path


# ============================================================
# DATABASE RESET
# ============================================================

def reset_database() -> None:
    """
    Reset development data while preserving the schema.
    """

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    backup_path = create_backup()

    print("=" * 60)
    print("OFFLINE COMM SYSTEM - DEVELOPMENT DATABASE RESET")
    print("=" * 60)
    print()
    print(f"Database : {DATABASE_PATH}")
    print(f"Backup   : {backup_path}")
    print()

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        # ----------------------------------------------------
        # Remove communication records.
        # ----------------------------------------------------

        cursor.execute(
            "DELETE FROM messages"
        )

        cursor.execute(
            "DELETE FROM locations"
        )

        cursor.execute(
            "DELETE FROM resource_requests"
        )

        cursor.execute(
            "DELETE FROM sos_alerts"
        )

        # ----------------------------------------------------
        # Remove network nodes.
        # ----------------------------------------------------

        cursor.execute(
            "DELETE FROM nodes"
        )

        # ----------------------------------------------------
        # Remove users.
        # ----------------------------------------------------

        cursor.execute(
            "DELETE FROM users"
        )

        # ----------------------------------------------------
        # Reset AUTOINCREMENT sequences where available.
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM sqlite_sequence
            WHERE name IN (
                'users',
                'nodes',
                'messages',
                'locations',
                'resource_requests',
                'sos_alerts'
            )
            """
        )

        # ----------------------------------------------------
        # Create clean development users.
        # ----------------------------------------------------

        timestamp = current_timestamp()

        for user in DEVELOPMENT_USERS:

            cursor.execute(
                """
                INSERT INTO users (
                    user_name,
                    created_at,
                    node_id
                )
                VALUES (?, ?, ?)
                """,
                (
                    user["user_name"],
                    timestamp,
                    user["node_id"],
                ),
            )

        connection.commit()

        # ----------------------------------------------------
        # Verify users.
        # ----------------------------------------------------

        users = cursor.execute(
            """
            SELECT
                id,
                user_name,
                created_at,
                node_id
            FROM users
            ORDER BY id
            """
        ).fetchall()

        # ----------------------------------------------------
        # Verify counts.
        # ----------------------------------------------------

        messages_count = cursor.execute(
            "SELECT COUNT(*) FROM messages"
        ).fetchone()[0]

        nodes_count = cursor.execute(
            "SELECT COUNT(*) FROM nodes"
        ).fetchone()[0]

        locations_count = cursor.execute(
            "SELECT COUNT(*) FROM locations"
        ).fetchone()[0]

        resource_count = cursor.execute(
            "SELECT COUNT(*) FROM resource_requests"
        ).fetchone()[0]

        sos_count = cursor.execute(
            "SELECT COUNT(*) FROM sos_alerts"
        ).fetchone()[0]

        # ----------------------------------------------------
        # Display result.
        # ----------------------------------------------------

        print("RESET COMPLETE")
        print()
        print("USERS")
        print("-" * 60)

        for user in users:
            print(
                f"ID={user['id']} | "
                f"NAME={user['user_name']} | "
                f"NODE={user['node_id']} | "
                f"CREATED={user['created_at']}"
            )

        print()
        print("DATABASE COUNTS")
        print("-" * 60)
        print(f"Users             : {len(users)}")
        print(f"Messages          : {messages_count}")
        print(f"Nodes             : {nodes_count}")
        print(f"Locations         : {locations_count}")
        print(f"Resource requests : {resource_count}")
        print(f"SOS alerts        : {sos_count}")
        print()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    reset_database()
