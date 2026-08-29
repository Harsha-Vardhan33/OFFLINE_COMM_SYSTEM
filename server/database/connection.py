"""
OFFLINE COMM SYSTEM
Database Connection Management
"""

import sqlite3

from server.config import DATABASE_PATH


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a SQLite database connection.

    Row factory is enabled so database rows can be converted
    directly into dictionaries.
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection
