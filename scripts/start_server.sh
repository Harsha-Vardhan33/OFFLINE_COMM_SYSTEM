#!/bin/bash

# ============================================================
# OFFLINE COMM SYSTEM
# Server Start Script
#
# Purpose:
#   Start the OFFLINE_COMM_SYSTEM Flask server locally.
#
# This script is intended for normal server operation after
# the one-time setup has been completed.
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo
echo "============================================================"
echo " OFFLINE COMM SYSTEM"
echo " SERVER START"
echo "============================================================"
echo

# ============================================================
# CHECK PROJECT
# ============================================================

if [ ! -f "$PROJECT_DIR/server/app.py" ]; then

    echo "ERROR: Server application not found."

    echo "Expected:"
    echo "$PROJECT_DIR/server/app.py"

    exit 1

fi


# ============================================================
# CHECK VIRTUAL ENVIRONMENT
# ============================================================

if [ ! -f "$VENV_DIR/bin/activate" ]; then

    echo "ERROR: Python virtual environment not found."

    echo "Run first:"
    echo

    echo "./scripts/setup_server.sh"

    exit 1

fi


# ============================================================
# ACTIVATE VIRTUAL ENVIRONMENT
# ============================================================

source "$VENV_DIR/bin/activate"


# ============================================================
# MOVE TO PROJECT ROOT
# ============================================================

cd "$PROJECT_DIR"


# ============================================================
# CHECK FLASK INSTALLATION
# ============================================================

if ! python -c "import flask" >/dev/null 2>&1; then

    echo "ERROR: Flask is not installed in the virtual environment."

    echo "Run:"
    echo

    echo "./scripts/setup_server.sh"

    exit 1

fi


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

echo "Initializing database..."

python -c "
from server.database.schema import initialize_database
initialize_database()
print('Database ready.')
"


# ============================================================
# SERVER INFORMATION
# ============================================================

echo
echo "Python:"
python --version

echo
echo "Project:"
echo "$PROJECT_DIR"

echo
echo "Server address:"
echo "http://0.0.0.0:5000"

echo
echo "Local:"
echo "http://127.0.0.1:5000"


# ============================================================
# LAN IP
# ============================================================

LAN_IP=$(hostname -I | awk '{print $1}')

if [ -n "$LAN_IP" ]; then

    echo
    echo "LAN:"
    echo "http://$LAN_IP:5000"

fi


# ============================================================
# START SERVER
# ============================================================

echo
echo "============================================================"
echo " STARTING FLASK SERVER"
echo "============================================================"
echo
echo "Press CTRL+C to stop the server."
echo

exec python -m server.app
