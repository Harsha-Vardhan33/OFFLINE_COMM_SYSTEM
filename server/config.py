"""
OFFLINE COMM SYSTEM
Server Configuration
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

SERVER_DIR = Path(__file__).resolve().parent

PROJECT_DIR = SERVER_DIR.parent

DATABASE_DIR = SERVER_DIR / "database"

DATABASE_PATH = DATABASE_DIR / "offline_comm.db"


# ============================================================
# SERVER
# ============================================================

SERVER_HOST = "0.0.0.0"

SERVER_PORT = 5000

DEBUG = True


# ============================================================
# SYSTEM INFORMATION
# ============================================================

SYSTEM_NAME = "OFFLINE_COMM_SYSTEM"

SYSTEM_VERSION = "1.0.0"


# ============================================================
# NODE SETTINGS
# ============================================================

DEFAULT_NODE_ROLE = "NODE"

DEFAULT_NODE_STATUS = "ONLINE"


# ============================================================
# COMMUNICATION SETTINGS
# ============================================================

DEFAULT_MESSAGE_TYPE = "TEXT"

DEFAULT_MESSAGE_STATUS = "RECEIVED"


# ============================================================
# SOS SETTINGS
# ============================================================

DEFAULT_SOS_PRIORITY = "HIGH"

DEFAULT_SOS_STATUS = "ACTIVE"


# ============================================================
# RESOURCE SETTINGS
# ============================================================

DEFAULT_RESOURCE_PRIORITY = "NORMAL"

DEFAULT_RESOURCE_STATUS = "PENDING"
