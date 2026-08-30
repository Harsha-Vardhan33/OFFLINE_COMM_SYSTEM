"""
OFFLINE COMM SYSTEM
Flask Application Entry Point
"""

from flask import (
    Flask,
    jsonify,
    render_template,
    redirect
)

from server.config import (
    DEBUG,
    SERVER_HOST,
    SERVER_PORT,
    SYSTEM_NAME
)

from server.database.schema import (
    initialize_database
)

from server.api.health import health_api
from server.api.nodes import nodes_api
from server.api.sos import sos_api
from server.api.messages import messages_api
from server.api.locations import locations_api
from server.api.resources import resources_api


# ============================================================
# APPLICATION FACTORY
# ============================================================

def create_app():

    app = Flask(__name__)

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    initialize_database()

    # --------------------------------------------------------
    # API BLUEPRINTS
    # --------------------------------------------------------

    app.register_blueprint(health_api)
    app.register_blueprint(nodes_api)
    app.register_blueprint(sos_api)
    app.register_blueprint(messages_api)
    app.register_blueprint(locations_api)
    app.register_blueprint(resources_api)

    # ========================================================
    # CAPTIVE PORTAL
    # ========================================================

    @app.get("/")
    def portal():

        return render_template(
            "portal.html",
            system_name=SYSTEM_NAME
        )

    # --------------------------------------------------------
    # Android connectivity check
    #
    # Android commonly checks /generate_204.
    # A normal Internet connection returns HTTP 204.
    #
    # For our offline network, returning the portal instead
    # tells the client that authentication/captive access is
    # required.
    # --------------------------------------------------------

    @app.get("/generate_204")
    def android_generate_204():

        return redirect("/", code=302)

    # --------------------------------------------------------
    # Apple captive portal detection
    # --------------------------------------------------------

    @app.get("/hotspot-detect.html")
    def apple_hotspot_detect():

        return redirect("/", code=302)

    # --------------------------------------------------------
    # Windows connectivity check
    # --------------------------------------------------------

    @app.get("/connecttest.txt")
    def windows_connect_test():

        return redirect("/", code=302)

    # --------------------------------------------------------
    # Windows NCSI
    # --------------------------------------------------------

    @app.get("/ncsi.txt")
    def windows_ncsi():

        return redirect("/", code=302)

    # --------------------------------------------------------
    # Microsoft connectivity check variant
    # --------------------------------------------------------

    @app.get("/connecttest.txt/")
    def windows_connect_test_slash():

        return redirect("/", code=302)

    # ========================================================
    # DASHBOARD
    # ========================================================

    @app.get("/dashboard")
    def dashboard():

        return render_template(
            "dashboard.html",
            system_name=SYSTEM_NAME
        )

    # ========================================================
    # SERVER INFORMATION API
    # ========================================================

    @app.get("/api")
    def api_root():

        return jsonify({
            "system": SYSTEM_NAME,
            "message": "Offline Emergency Communication Server",
            "status": "running"
        })

    # ========================================================
    # CAPTIVE PORTAL STATUS
    # ========================================================

    @app.get("/api/portal")
    def portal_status():

        return jsonify({
            "system": SYSTEM_NAME,
            "portal": "enabled",
            "network": "OFFLINE_COMM",
            "internet_required": False,
            "status": "running"
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
        " Captive portal: ENABLED"
    )

    print(
        " Portal: http://10.42.0.1:5000/"
    )

    print(
        " Dashboard: http://10.42.0.1:5000/dashboard"
    )

    print(
        "----------------------------------------------"
    )

    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=DEBUG
    )