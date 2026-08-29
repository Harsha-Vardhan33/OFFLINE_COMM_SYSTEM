"""
OFFLINE COMM SYSTEM
Resource Request API
"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from server.config import (
    DEFAULT_RESOURCE_PRIORITY,
    DEFAULT_RESOURCE_STATUS
)

from server.database.connection import get_connection


resources_api = Blueprint(
    "resources_api",
    __name__
)


# ============================================================
# GET RESOURCE REQUESTS
# ============================================================

@resources_api.get("/api/resources")
def get_resources():

    connection = get_connection()


    rows = connection.execute(
        """
        SELECT
            id,
            node_id,
            user_name,
            resource,
            quantity,
            priority,
            status,
            created_at
        FROM resource_requests
        ORDER BY created_at DESC
        """
    ).fetchall()


    connection.close()


    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# CREATE RESOURCE REQUEST
# ============================================================

@resources_api.post("/api/resources")
def create_resource():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "error":
                "JSON data required"

        }), 400


    resource = data.get(
        "resource"
    )


    if not resource:

        return jsonify({

            "success": False,

            "error":
                "resource is required"

        }), 400


    now = datetime.now().isoformat()


    connection = get_connection()


    cursor = connection.execute(
        """
        INSERT INTO resource_requests (

            node_id,
            user_name,
            resource,
            quantity,
            priority,
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
                "user_name"
            ),

            resource,

            data.get(
                "quantity",
                1
            ),

            data.get(
                "priority",
                DEFAULT_RESOURCE_PRIORITY
            ),

            data.get(
                "status",
                DEFAULT_RESOURCE_STATUS
            ),

            now

        )
    )


    connection.commit()


    resource_id = cursor.lastrowid


    connection.close()


    return jsonify({

        "success": True,

        "message":
            "Resource request stored",

        "id":
            resource_id

    }), 201


# ============================================================
# UPDATE RESOURCE STATUS
# ============================================================

@resources_api.put(
    "/api/resources/<int:resource_id>"
)
def update_resource(resource_id):

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
        UPDATE resource_requests

        SET status = ?

        WHERE id = ?
        """,

        (

            data.get(
                "status"
            ),

            resource_id

        )
    )


    connection.commit()

    connection.close()


    if cursor.rowcount == 0:

        return jsonify({

            "success": False,

            "error":
                "Resource request not found"

        }), 404


    return jsonify({

        "success": True,

        "message":
            "Resource status updated"

    })
