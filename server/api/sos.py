"""
OFFLINE COMM SYSTEM
SOS API
"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from server.config import (
    DEFAULT_SOS_PRIORITY,
    DEFAULT_SOS_STATUS
)

from server.database.connection import get_connection


sos_api = Blueprint(
    "sos_api",
    __name__
)


# ============================================================
# GET SOS ALERTS
# ============================================================

@sos_api.get("/api/sos")
def get_sos():

    connection = get_connection()


    rows = connection.execute(
        """
        SELECT
            id,
            node_id,
            user_name,
            message,
            latitude,
            longitude,
            priority,
            status,
            created_at
        FROM sos_alerts
        ORDER BY created_at DESC
        """
    ).fetchall()


    connection.close()


    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# CREATE SOS
# ============================================================

@sos_api.post("/api/sos")
def create_sos():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "error":
                "JSON data required"

        }), 400


    now = datetime.now().isoformat()


    connection = get_connection()


    cursor = connection.execute(
        """
        INSERT INTO sos_alerts (

            node_id,
            user_name,
            message,
            latitude,
            longitude,
            priority,
            status,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (

            data.get(
                "node_id"
            ),

            data.get(
                "user_name"
            ),

            data.get(
                "message"
            ),

            data.get(
                "latitude"
            ),

            data.get(
                "longitude"
            ),

            data.get(
                "priority",
                DEFAULT_SOS_PRIORITY
            ),

            data.get(
                "status",
                DEFAULT_SOS_STATUS
            ),

            now

        )
    )


    connection.commit()


    alert_id = cursor.lastrowid


    connection.close()


    return jsonify({

        "success": True,

        "message":
            "SOS alert created",

        "id":
            alert_id

    }), 201


# ============================================================
# UPDATE SOS STATUS
# ============================================================

@sos_api.put("/api/sos/<int:alert_id>")
def update_sos(alert_id):

    data = request.get_json(
        silent=True
    )


    if not data or not data.get(
        "status"
    ):

        return jsonify({

            "success": False,

            "error":
                "status is required"

        }), 400


    connection = get_connection()


    cursor = connection.execute(
        """
        UPDATE sos_alerts

        SET status = ?

        WHERE id = ?
        """,

        (

            data.get(
                "status"
            ),

            alert_id

        )
    )


    connection.commit()

    connection.close()


    if cursor.rowcount == 0:

        return jsonify({

            "success": False,

            "error":
                "SOS alert not found"

        }), 404


    return jsonify({

        "success": True,

        "message":
            "SOS status updated"

    })
