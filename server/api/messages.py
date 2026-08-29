"""
OFFLINE COMM SYSTEM
Message API
"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from server.config import (
    DEFAULT_MESSAGE_STATUS,
    DEFAULT_MESSAGE_TYPE
)

from server.database.connection import get_connection


messages_api = Blueprint(
    "messages_api",
    __name__
)


# ============================================================
# GET MESSAGES
# ============================================================

@messages_api.get("/api/messages")
def get_messages():

    connection = get_connection()


    rows = connection.execute(
        """
        SELECT
            id,
            node_id,
            sender,
            receiver,
            message,
            message_type,
            status,
            created_at
        FROM messages
        ORDER BY created_at DESC
        """
    ).fetchall()


    connection.close()


    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# CREATE MESSAGE
# ============================================================

@messages_api.post("/api/messages")
def create_message():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "error":
                "JSON data required"

        }), 400


    message = data.get(
        "message"
    )


    if not message:

        return jsonify({

            "success": False,

            "error":
                "message is required"

        }), 400


    now = datetime.now().isoformat()


    connection = get_connection()


    cursor = connection.execute(
        """
        INSERT INTO messages (

            node_id,
            sender,
            receiver,
            message,
            message_type,
            status,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,

        (

            data.get(
                "node_id"
            ),

            data.get(
                "sender"
            ),

            data.get(
                "receiver"
            ),

            message,

            data.get(
                "message_type",
                DEFAULT_MESSAGE_TYPE
            ),

            data.get(
                "status",
                DEFAULT_MESSAGE_STATUS
            ),

            now

        )
    )


    connection.commit()


    message_id = cursor.lastrowid


    connection.close()


    return jsonify({

        "success": True,

        "message":
            "Message stored",

        "id":
            message_id

    }), 201
