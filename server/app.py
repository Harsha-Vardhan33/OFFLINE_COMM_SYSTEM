from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
from pathlib import Path


# ============================================================
# OFFLINE COMM SYSTEM
# ESP32 Mesh-Based Offline Emergency Communication System
# ============================================================

app = Flask(__name__)

# Keep the database in the project/server directory.
# This avoids problems caused by running the application
# from different working directories.
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "offline_comm.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    db = sqlite3.connect(DATABASE)

    # Allows:
    # row["column_name"]
    # instead of:
    # row[0], row[1], etc.
    db.row_factory = sqlite3.Row

    return db


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_database():

    db = get_connection()

    # --------------------------------------------------------
    # SOS ALERTS TABLE
    # --------------------------------------------------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS sos_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            user_name TEXT,
            message TEXT,
            latitude REAL,
            longitude REAL,
            priority TEXT DEFAULT 'HIGH',
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT
        )
    """)

    # --------------------------------------------------------
    # MESSAGES TABLE
    # --------------------------------------------------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            message_type TEXT DEFAULT 'TEXT',
            status TEXT DEFAULT 'RECEIVED',
            created_at TEXT
        )
    """)

    # --------------------------------------------------------
    # LOCATIONS TABLE
    # --------------------------------------------------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            user_name TEXT,
            latitude REAL,
            longitude REAL,
            accuracy REAL,
            created_at TEXT
        )
    """)

    # --------------------------------------------------------
    # RESOURCE REQUESTS TABLE
    # --------------------------------------------------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS resource_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            user_name TEXT,
            resource TEXT,
            quantity INTEGER DEFAULT 1,
            priority TEXT DEFAULT 'NORMAL',
            status TEXT DEFAULT 'PENDING',
            created_at TEXT
        )
    """)

    # --------------------------------------------------------
    # ESP32 NODES TABLE
    # --------------------------------------------------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            node_id TEXT PRIMARY KEY,
            node_name TEXT,
            ip_address TEXT,
            role TEXT DEFAULT 'NODE',
            status TEXT DEFAULT 'ONLINE',
            battery REAL,
            signal_strength REAL,
            last_seen TEXT
        )
    """)

    db.commit()
    db.close()


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def home():

    return render_template("dashboard.html")


# ============================================================
# SERVER INFORMATION
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "OK",
        "server": "OFFLINE_COMM_SYSTEM",
        "time": datetime.now().isoformat()
    })


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.route("/api/status", methods=["GET"])
def system_status():

    db = get_connection()

    sos_count = db.execute("""
        SELECT COUNT(*)
        FROM sos_alerts
        WHERE status = 'ACTIVE'
    """).fetchone()[0]

    message_count = db.execute("""
        SELECT COUNT(*)
        FROM messages
    """).fetchone()[0]

    resource_count = db.execute("""
        SELECT COUNT(*)
        FROM resource_requests
        WHERE status = 'PENDING'
    """).fetchone()[0]

    online_nodes = db.execute("""
        SELECT COUNT(*)
        FROM nodes
        WHERE status = 'ONLINE'
    """).fetchone()[0]

    total_nodes = db.execute("""
        SELECT COUNT(*)
        FROM nodes
    """).fetchone()[0]

    db.close()

    return jsonify({
        "server": "ONLINE",
        "active_sos": sos_count,
        "total_messages": message_count,
        "pending_resources": resource_count,
        "online_nodes": online_nodes,
        "total_nodes": total_nodes,
        "database": "ONLINE",
        "last_updated": datetime.now().isoformat()
    })


# ============================================================
# GET SOS ALERTS
# ============================================================

@app.route("/api/sos", methods=["GET"])
def get_sos_alerts():

    db = get_connection()

    alerts = db.execute("""
        SELECT *
        FROM sos_alerts
        ORDER BY created_at DESC
    """).fetchall()

    db.close()

    return jsonify([
        dict(alert)
        for alert in alerts
    ])


# ============================================================
# CREATE SOS ALERT
# ============================================================

@app.route("/api/sos", methods=["POST"])
def create_sos_alert():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "JSON data required"
        }), 400

    created_at = datetime.now().isoformat()

    db = get_connection()

    cursor = db.execute("""
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
    """, (
        data.get("node_id"),
        data.get("user_name"),
        data.get("message"),
        data.get("latitude"),
        data.get("longitude"),
        data.get("priority", "HIGH"),
        data.get("status", "ACTIVE"),
        created_at
    ))

    db.commit()

    alert_id = cursor.lastrowid

    db.close()

    return jsonify({
        "success": True,
        "message": "SOS alert created",
        "id": alert_id
    }), 201


# ============================================================
# UPDATE SOS STATUS
# ============================================================

@app.route("/api/sos/<int:alert_id>", methods=["PUT"])
def update_sos_status(alert_id):

    data = request.get_json()

    if not data or not data.get("status"):

        return jsonify({
            "error": "status is required"
        }), 400

    db = get_connection()

    cursor = db.execute("""
        UPDATE sos_alerts
        SET status = ?
        WHERE id = ?
    """, (
        data.get("status"),
        alert_id
    ))

    db.commit()

    updated = cursor.rowcount

    db.close()

    if updated == 0:

        return jsonify({
            "error": "SOS alert not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "SOS status updated"
    })


# ============================================================
# GET MESSAGES
# ============================================================

@app.route("/api/messages", methods=["GET"])
def get_messages():

    db = get_connection()

    messages = db.execute("""
        SELECT *
        FROM messages
        ORDER BY created_at DESC
    """).fetchall()

    db.close()

    return jsonify([
        dict(message)
        for message in messages
    ])


# ============================================================
# CREATE MESSAGE
# ============================================================

@app.route("/api/messages", methods=["POST"])
def create_message():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "JSON data required"
        }), 400

    if not data.get("message"):

        return jsonify({
            "error": "message is required"
        }), 400

    created_at = datetime.now().isoformat()

    db = get_connection()

    cursor = db.execute("""
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
    """, (
        data.get("node_id"),
        data.get("sender"),
        data.get("receiver"),
        data.get("message"),
        data.get("message_type", "TEXT"),
        data.get("status", "RECEIVED"),
        created_at
    ))

    db.commit()

    message_id = cursor.lastrowid

    db.close()

    return jsonify({
        "success": True,
        "message": "Message stored",
        "id": message_id
    }), 201


# ============================================================
# GET LOCATIONS
# ============================================================

@app.route("/api/locations", methods=["GET"])
def get_locations():

    db = get_connection()

    locations = db.execute("""
        SELECT *
        FROM locations
        ORDER BY created_at DESC
    """).fetchall()

    db.close()

    return jsonify([
        dict(location)
        for location in locations
    ])


# ============================================================
# CREATE LOCATION
# ============================================================

@app.route("/api/locations", methods=["POST"])
def create_location():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "JSON data required"
        }), 400

    if data.get("latitude") is None or data.get("longitude") is None:

        return jsonify({
            "error": "latitude and longitude are required"
        }), 400

    created_at = datetime.now().isoformat()

    db = get_connection()

    cursor = db.execute("""
        INSERT INTO locations (
            node_id,
            user_name,
            latitude,
            longitude,
            accuracy,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("node_id"),
        data.get("user_name"),
        data.get("latitude"),
        data.get("longitude"),
        data.get("accuracy"),
        created_at
    ))

    db.commit()

    location_id = cursor.lastrowid

    db.close()

    return jsonify({
        "success": True,
        "message": "Location stored",
        "id": location_id
    }), 201


# ============================================================
# GET RESOURCE REQUESTS
# ============================================================

@app.route("/api/resources", methods=["GET"])
def get_resources():

    db = get_connection()

    resources = db.execute("""
        SELECT *
        FROM resource_requests
        ORDER BY created_at DESC
    """).fetchall()

    db.close()

    return jsonify([
        dict(resource)
        for resource in resources
    ])


# ============================================================
# CREATE RESOURCE REQUEST
# ============================================================

@app.route("/api/resources", methods=["POST"])
def create_resource():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "JSON data required"
        }), 400

    if not data.get("resource"):

        return jsonify({
            "error": "resource is required"
        }), 400

    created_at = datetime.now().isoformat()

    db = get_connection()

    cursor = db.execute("""
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
    """, (
        data.get("node_id"),
        data.get("user_name"),
        data.get("resource"),
        data.get("quantity", 1),
        data.get("priority", "NORMAL"),
        data.get("status", "PENDING"),
        created_at
    ))

    db.commit()

    resource_id = cursor.lastrowid

    db.close()

    return jsonify({
        "success": True,
        "message": "Resource request stored",
        "id": resource_id
    }), 201


# ============================================================
# UPDATE RESOURCE STATUS
# ============================================================

@app.route("/api/resources/<int:resource_id>", methods=["PUT"])
def update_resource_status(resource_id):

    data = request.get_json()

    if not data or not data.get("status"):

        return jsonify({
            "error": "status is required"
        }), 400

    db = get_connection()

    cursor = db.execute("""
        UPDATE resource_requests
        SET status = ?
        WHERE id = ?
    """, (
        data.get("status"),
        resource_id
    ))

    db.commit()

    updated = cursor.rowcount

    db.close()

    if updated == 0:

        return jsonify({
            "error": "Resource request not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Resource status updated"
    })


# ============================================================
# GET ESP32 NODES
# ============================================================

@app.route("/api/nodes", methods=["GET"])
def get_nodes():

    db = get_connection()

    nodes = db.execute("""
        SELECT *
        FROM nodes
        ORDER BY node_id
    """).fetchall()

    db.close()

    return jsonify([
        dict(node)
        for node in nodes
    ])


# ============================================================
# REGISTER / UPDATE ESP32 NODE
# ============================================================

@app.route("/api/nodes", methods=["POST"])
def register_node():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "JSON data required"
        }), 400

    node_id = data.get("node_id")

    if not node_id:

        return jsonify({
            "error": "node_id is required"
        }), 400

    last_seen = datetime.now().isoformat()

    db = get_connection()

    db.execute("""
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
            node_name = excluded.node_name,
            ip_address = excluded.ip_address,
            role = excluded.role,
            status = excluded.status,
            battery = excluded.battery,
            signal_strength = excluded.signal_strength,
            last_seen = excluded.last_seen
    """, (
        node_id,
        data.get("node_name"),
        data.get("ip_address"),
        data.get("role", "NODE"),
        data.get("status", "ONLINE"),
        data.get("battery"),
        data.get("signal_strength"),
        last_seen
    ))

    db.commit()
    db.close()

    return jsonify({
        "success": True,
        "message": "Node registered/updated",
        "node_id": node_id
    })


# ============================================================
# SERVER START
# ============================================================

if __name__ == "__main__":

    init_database()

    print("----------------------------------------------")
    print(" OFFLINE COMM SYSTEM")
    print("----------------------------------------------")
    print(" Server starting...")
    print(" Database:", DATABASE)
    print("----------------------------------------------")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )