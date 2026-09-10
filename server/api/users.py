"""
OFFLINE COMM SYSTEM
User Registration API
"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from server.database.connection import get_connection


users_api = Blueprint(
    "users_api",
    __name__
)


# ============================================================
# GET ALL USERS
# ============================================================

@users_api.get("/api/users")
def get_users():

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT
                id,
                user_name,
                node_id,
                created_at
            FROM users
            ORDER BY id DESC
            """
        ).fetchall()

        return jsonify([
            dict(row)
            for row in rows
        ])

    finally:

        connection.close()


# ============================================================
# GET USER BY NODE
# ============================================================

@users_api.get("/api/users/<node_id>")
def get_user_by_node(
    node_id
):

    node_id = node_id.strip()

    if not node_id:

        return jsonify({
            "success": False,
            "error": "node_id is required"
        }), 400


    connection = get_connection()

    try:

        row = connection.execute(
            """
            SELECT
                id,
                user_name,
                node_id,
                created_at
            FROM users
            WHERE node_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                node_id,
            )
        ).fetchone()


        if not row:

            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404


        return jsonify(
            dict(row)
        )

    finally:

        connection.close()


# ============================================================
# REGISTER / UPDATE USER
# ============================================================

@users_api.post("/api/users")
def register_user():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({
            "success": False,
            "error": "JSON data required"
        }), 400


    user_name = str(
        data.get(
            "user_name",
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

    if not user_name:

        return jsonify({
            "success": False,
            "error": "user_name is required"
        }), 400


    if len(user_name) < 2:

        return jsonify({
            "success": False,
            "error":
                "user_name must contain at least 2 characters"
        }), 400


    if len(user_name) > 80:

        return jsonify({
            "success": False,
            "error":
                "user_name must not exceed 80 characters"
        }), 400


    if not node_id:

        return jsonify({
            "success": False,
            "error": "node_id is required"
        }), 400


    if len(node_id) > 64:

        return jsonify({
            "success": False,
            "error":
                "node_id must not exceed 64 characters"
        }), 400


    created_at = datetime.now().isoformat()


    connection = get_connection()

    try:

        # ====================================================
        # CHECK EXISTING DEVICE
        # ====================================================

        existing = connection.execute(
            """
            SELECT
                id,
                user_name,
                node_id,
                created_at
            FROM users
            WHERE node_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                node_id,
            )
        ).fetchone()


        # ====================================================
        # EXISTING DEVICE
        # ====================================================

        if existing:

            connection.execute(
                """
                UPDATE users
                SET
                    user_name = ?
                WHERE id = ?
                """,
                (
                    user_name,
                    existing["id"]
                )
            )


            connection.commit()


            return jsonify({

                "success": True,

                "message":
                    "User updated",

                "user_id":
                    existing["id"],

                "user_name":
                    user_name,

                "node_id":
                    node_id,

                "existing":
                    True

            }), 200


        # ====================================================
        # NEW DEVICE
        # ====================================================

        cursor = connection.execute(
            """
            INSERT INTO users (
                user_name,
                node_id,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                user_name,
                node_id,
                created_at
            )
        )


        connection.commit()


        return jsonify({

            "success": True,

            "message":
                "User registered",

            "user_id":
                cursor.lastrowid,

            "user_name":
                user_name,

            "node_id":
                node_id,

            "existing":
                False

        }), 201


    except Exception as error:

        connection.rollback()

        return jsonify({

            "success": False,

            "error":
                "Unable to register user",

            "details":
                str(error)

        }), 500


    finally:

        connection.close()
