"""
OFFLINE COMM SYSTEM
Location API
"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from server.database.connection import get_connection


locations_api = Blueprint(
    "locations_api",
    __name__
)


# ============================================================
# GET LOCATIONS
# ============================================================

@locations_api.get("/api/locations")
def get_locations():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            node_id,
            user_name,
            latitude,
            longitude,
            accuracy,
            created_at
        FROM locations
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# CREATE LOCATION
# ============================================================

@locations_api.post("/api/locations")
def create_location():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "success": False,

            "error":
                "JSON data required"

        }), 400


    latitude = data.get(
        "latitude"
    )

    longitude = data.get(
        "longitude"
    )


    if latitude is None or longitude is None:

        return jsonify({

            "success": False,

            "error":
                "latitude and longitude are required"

        }), 400


    now = datetime.now().isoformat()


    connection = get_connection()


    cursor = connection.execute(
        """
        INSERT INTO locations (

            node_id,
            user_name,
            latitude,
            longitude,
            accuracy,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,

        (

            data.get(
                "node_id"
            ),

            data.get(
                "user_name"
            ),

            latitude,

            longitude,

            data.get(
                "accuracy"
            ),

            now

        )
    )


    connection.commit()


    location_id = cursor.lastrowid


    connection.close()


    return jsonify({

        "success": True,

        "message":
            "Location stored",

        "id":
            location_id

    }), 201
