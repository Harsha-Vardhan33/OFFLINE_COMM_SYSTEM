"""
OFFLINE COMM SYSTEM
Flask Application Entry Point
"""

from flask import Flask, jsonify

from server.config import (
    DEBUG,
    SERVER_HOST,
    SERVER_PORT,
    SYSTEM_NAME
)

from server.database.schema import (
    initialize_database
)

from server.api.health import (
    health_api
)

from server.api.nodes import (
    nodes_api
)

from server.api.sos import (
    sos_api
)

from server.api.messages import (
    messages_api
)

from server.api.locations import (
    locations_api
)

from server.api.resources import (
    resources_api
)


# ============================================================
# APPLICATION FACTORY
# ============================================================

def create_app():

    app = Flask(
        __name__
    )


    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    initialize_database()


    # --------------------------------------------------------
    # API BLUEPRINTS
    # --------------------------------------------------------

    app.register_blueprint(
        health_api
    )

    app.register_blueprint(
        nodes_api
    )

    app.register_blueprint(
        sos_api
    )

    app.register_blueprint(
        messages_api
    )

    app.register_blueprint(
        locations_api
    )

    app.register_blueprint(
        resources_api
    )


    # --------------------------------------------------------
    # ROOT ENDPOINT
    # --------------------------------------------------------

    @app.get("/")
    def root():

        return jsonify({

            "system":
                SYSTEM_NAME,

            "message":
                "Offline Emergency Communication Server",

            "status":
                "running"

        })


    return app


# ============================================================
# APPLICATION INSTANCE
# ============================================================

app = create_app()


# ============================================================
# SERVER START
# ============================================================

if __name__ == "__main__":

    print(
        "----------------------------------------------"
    )

    print(
        " OFFLINE COMM SYSTEM"
    )

    print(
        "----------------------------------------------"
    )

    print(
        " Server starting..."
    )

    print(
        " Database initialized"
    )

    print(
        " Host:",
        SERVER_HOST
    )

    print(
        " Port:",
        SERVER_PORT
    )

    print(
        "----------------------------------------------"
    )


    app.run(

        host=SERVER_HOST,

        port=SERVER_PORT,

        debug=DEBUG

    )
