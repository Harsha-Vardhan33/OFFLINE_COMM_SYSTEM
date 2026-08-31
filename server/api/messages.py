"""
OFFLINE COMM SYSTEM
User-to-User Message API
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
# GET ALL MESSAGES
# ============================================================

@messages_api.get("/api/messages")
def get_messages():

    connection = get_connection()

    try:

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
            ORDER BY created_at ASC, id ASC
            """
        ).fetchall()

        return jsonify([
            dict(row)
            for row in rows
        ])

    finally:

        connection.close()


# ============================================================
# GET ONE-TO-ONE CONVERSATION
# ============================================================

@messages_api.get(
    "/api/messages/conversation"
)
def get_conversation():

    sender = str(
        request.args.get(
            "sender",
            ""
        )
    ).strip()

    receiver = str(
        request.args.get(
            "receiver",
            ""
        )
    ).strip()

    if not sender:

        return jsonify({
            "success": False,
            "error": "sender is required"
        }), 400

    if not receiver:

        return jsonify({
            "success": False,
            "error": "receiver is required"
        }), 400

    if sender == receiver:

        return jsonify({
            "success": False,
            "error":
                "sender and receiver must be different"
        }), 400

    connection = get_connection()

    try:

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
            WHERE
                (
                    sender = ?
                    AND receiver = ?
                )
                OR
                (
                    sender = ?
                    AND receiver = ?
                )
            ORDER BY
                created_at ASC,
                id ASC
            """,
            (
                sender,
                receiver,
                receiver,
                sender
            )
        ).fetchall()

        return jsonify([
            dict(row)
            for row in rows
        ])

    finally:

        connection.close()


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
            "error": "JSON data required"
        }), 400

    sender = str(
        data.get(
            "sender",
            ""
        )
    ).strip()

    receiver = str(
        data.get(
            "receiver",
            ""
        )
    ).strip()

    message = str(
        data.get(
            "message",
            ""
        )
    ).strip()

    node_id = str(
        data.get(
            "node_id",
            ""
        )
    ).strip()

    # ========================================================
    # VALIDATION
    # ========================================================

    if not sender:

        return jsonify({
            "success": False,
            "error": "sender is required"
        }), 400

    if not receiver:

        return jsonify({
            "success": False,
            "error": "receiver is required"
        }), 400

    if sender == receiver:

        return jsonify({
            "success": False,
            "error":
                "sender and receiver must be different"
        }), 400

    if not message:

        return jsonify({
            "success": False,
            "error": "message is required"
        }), 400

    if len(message) > 10000:

        return jsonify({
            "success": False,
            "error":
                "message must not exceed 10000 characters"
        }), 400

    # ========================================================
    # DATABASE
    # ========================================================

    connection = get_connection()

    try:

        # ----------------------------------------------------
        # Verify sender exists
        # ----------------------------------------------------

        sender_exists = connection.execute(
            """
            SELECT
                id,
                user_name,
                node_id
            FROM users
            WHERE user_name = ?
            LIMIT 1
            """,
            (
                sender,
            )
        ).fetchone()

        if not sender_exists:

            return jsonify({
                "success": False,
                "error":
                    "Sender is not registered"
            }), 404

        # ----------------------------------------------------
        # Verify receiver exists
        # ----------------------------------------------------

        receiver_exists = connection.execute(
            """
            SELECT
                id,
                user_name,
                node_id
            FROM users
            WHERE user_name = ?
            LIMIT 1
            """,
            (
                receiver,
            )
        ).fetchone()

        if not receiver_exists:

            return jsonify({
                "success": False,
                "error":
                    "Receiver is not connected to the network"
            }), 404

        # ----------------------------------------------------
        # Create message
        # ----------------------------------------------------

        now = datetime.now().isoformat()

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
                node_id or None,
                sender,
                receiver,
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

        # ----------------------------------------------------
        # Read message back from database
        # ----------------------------------------------------

        row = connection.execute(
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
            WHERE id = ?
            """,
            (
                message_id,
            )
        ).fetchone()

        return jsonify({
            "success": True,
            "message": "Message stored",
            "data": dict(row)
        }), 201

    except Exception as error:

        connection.rollback()

        return jsonify({
            "success": False,
            "error":
                "Unable to store message",
            "details":
                str(error)
        }), 500

    finally:

        connection.close()
