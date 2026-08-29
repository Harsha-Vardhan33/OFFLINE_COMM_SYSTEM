"""
OFFLINE COMM SYSTEM
Health and System Status API
"""

from datetime import datetime

from flask import Blueprint, jsonify

from server.config import SYSTEM_NAME, SYSTEM_VERSION
from server.database.connection import get_connection


health_api = Blueprint(
    "health_api",
    __name__
)


# ============================================================
# HEALTH
# ============================================================

@health_api.get("/api/health")
def health():

    return jsonify({

        "status": "OK",

        "server": SYSTEM_NAME,

        "version": SYSTEM_VERSION,

        "time": datetime.now().isoformat()

    })


# ============================================================
# SYSTEM STATUS
# ============================================================

@health_api.get("/api/status")
def system_status():

    connection = get_connection()


    active_sos = connection.execute(
        """
        SELECT COUNT(*)
        FROM sos_alerts
        WHERE status = 'ACTIVE'
        """
    ).fetchone()[0]


    total_messages = connection.execute(
        """
        SELECT COUNT(*)
        FROM messages
        """
    ).fetchone()[0]


    pending_resources = connection.execute(
        """
        SELECT COUNT(*)
        FROM resource_requests
        WHERE status = 'PENDING'
        """
    ).fetchone()[0]


    online_nodes = connection.execute(
        """
        SELECT COUNT(*)
        FROM nodes
        WHERE status = 'ONLINE'
        """
    ).fetchone()[0]


    total_nodes = connection.execute(
        """
        SELECT COUNT(*)
        FROM nodes
        """
    ).fetchone()[0]


    connection.close()


    return jsonify({

        "server": "ONLINE",

        "database": "ONLINE",

        "active_sos": active_sos,

        "total_messages": total_messages,

        "pending_resources": pending_resources,

        "online_nodes": online_nodes,

        "total_nodes": total_nodes,

        "last_updated":
            datetime.now().isoformat()

    })

