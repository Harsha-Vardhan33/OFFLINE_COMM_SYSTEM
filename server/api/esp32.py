"""
OFFLINE COMMUNICATION SYSTEM

ESP32 API

Flask endpoints for communication with the ESP32 gateway.
"""


from flask import Blueprint, jsonify

from server.services.esp32_gateway import esp32_gateway


# ============================================================
# BLUEPRINT
# ============================================================

esp32_api = Blueprint(
    "esp32_api",
    __name__,
    url_prefix="/api/esp32"
)


# ============================================================
# PING
# ============================================================

@esp32_api.get("/ping")
def esp32_ping():

    result = esp32_gateway.ping()


    if result.get("success"):

        return jsonify({

            "status": "success",

            "device": "ESP32",

            "response":
                result.get("response", [])

        })


    return jsonify({

        "status": "error",

        "device": "ESP32",

        "error":
            result.get(
                "error",
                "ESP32 communication failed"
            )

    }), 503


# ============================================================
# STATUS
# ============================================================

@esp32_api.get("/status")
def esp32_status():

    result = esp32_gateway.status()


    if result.get("success"):

        return jsonify({

            "status": "success",

            "device": "ESP32",

            "response":
                result.get("response", [])

        })


    return jsonify({

        "status": "error",

        "device": "ESP32",

        "error":
            result.get(
                "error",
                "ESP32 communication failed"
            )

    }), 503


# ============================================================
# NODE ID
# ============================================================

@esp32_api.get("/id")
def esp32_id():

    result = esp32_gateway.get_id()


    if result.get("success"):

        return jsonify({

            "status": "success",

            "device": "ESP32",

            "response":
                result.get("response", [])

        })


    return jsonify({

        "status": "error",

        "device": "ESP32",

        "error":
            result.get(
                "error",
                "ESP32 communication failed"
            )

    }), 503
