"""
OFFLINE COMM SYSTEM
ESP32 Node API
"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from server.config import DEFAULT_NODE_ROLE
from server.database.connection import get_connection


nodes_api = Blueprint(
    "nodes_api",
    __name__
)


# ============================================================
# GET ALL NODES
# ============================================================

@nodes_api.get("/api/nodes")
def get_nodes():

    connection = get_connection()


    rows = connection.execute(
        """
        SELECT
            node_id,
            node_name,
            ip_address,
            role,
            status,
            battery,
            signal_strength,
            last_seen
        FROM nodes
        ORDER BY node_id
        """
    ).fetchall()


    connection.close()


    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# REGISTER / UPDATE NODE
# ============================================================

@nodes_api.post("/api/nodes")
def register_node():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "error":
                "JSON data required"

        }), 400


    node_id = data.get(
        "node_id"
    )


    if not node_id:

        return jsonify({

            "success": False,

            "error":
                "node_id is required"

        }), 400


    now = datetime.now().isoformat()


    connection = get_connection()


    connection.execute(
        """
        INSERT INTO nodes (

            node_id,
            node_name,
            ip_address,
            role,
            status,
            battery,
            signal_strength,
            last_seen

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(node_id)
        DO UPDATE SET

            node_name =
                excluded.node_name,

            ip_address =
                excluded.ip_address,

            role =
                excluded.role,

            status =
                excluded.status,

            battery =
                excluded.battery,

            signal_strength =
                excluded.signal_strength,

            last_seen =
                excluded.last_seen
        """,

        (

            node_id,

            data.get(
                "node_name"
            ),

            data.get(
                "ip_address"
            ),

            data.get(
                "role",
                DEFAULT_NODE_ROLE
            ),

            data.get(
                "status",
                "ONLINE"
            ),

            data.get(
                "battery"
            ),

            data.get(
                "signal_strength"
            ),

            now

        )
    )


    connection.commit()

    connection.close()


    return jsonify({

        "success": True,

        "message":
            "Node registered/updated",

        "node_id":
            node_id

    })
