#!/bin/bash

# ============================================================
# OFFLINE COMM SYSTEM
# Server Deployment Setup
#
# Purpose:
#   Prepare a Linux laptop to run OFFLINE_COMM_SYSTEM.
#
# Run this script ONCE while Internet is available.
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo
echo "============================================================"
echo " OFFLINE COMM SYSTEM"
echo " SERVER SETUP"
echo "============================================================"
echo

echo "Project directory:"
echo "$PROJECT_DIR"
echo


# ============================================================
# CHECK OPERATING SYSTEM
# ============================================================

if [ ! -f /etc/os-release ]; then
    echo "ERROR: Cannot identify operating system."
    exit 1
fi

. /etc/os-release

echo "Operating system:"
echo "$PRETTY_NAME"
echo


# ============================================================
# CHECK PYTHON
# ============================================================

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed."
    echo "Attempting installation..."

    if command -v apt >/dev/null 2>&1; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    else
        echo "ERROR: apt is unavailable."
        echo "Install Python 3 manually and run this script again."
        exit 1
    fi
fi

echo "Python:"
python3 --version
echo


# ============================================================
# CHECK PIP
# ============================================================

if ! python3 -m pip --version >/dev/null 2>&1; then

    echo "pip is not available."

    if command -v apt >/dev/null 2>&1; then
        sudo apt update
        sudo apt install -y python3-pip
    else
        echo "ERROR: Cannot install pip automatically."
        exit 1
    fi

fi

echo "pip:"
python3 -m pip --version
echo


# ============================================================
# CHECK VENV SUPPORT
# ============================================================

if ! python3 -m venv --help >/dev/null 2>&1; then

    echo "Python virtual environment support is missing."

    if command -v apt >/dev/null 2>&1; then
        sudo apt update
        sudo apt install -y python3-venv
    else
        echo "ERROR: Cannot install python3-venv."
        exit 1
    fi

fi


# ============================================================
# CREATE VIRTUAL ENVIRONMENT
# ============================================================

if [ ! -d "$VENV_DIR" ]; then

    echo "Creating Python virtual environment..."

    python3 -m venv "$VENV_DIR"

else

    echo "Virtual environment already exists."

fi

echo


# ============================================================
# ACTIVATE VIRTUAL ENVIRONMENT
# ============================================================

source "$VENV_DIR/bin/activate"

echo "Active Python:"
python --version
echo


# ============================================================
# UPGRADE PIP
# ============================================================

echo "Updating pip..."

python -m pip install --upgrade pip


# ============================================================
# INSTALL PROJECT DEPENDENCIES
# ============================================================

REQUIREMENTS="$PROJECT_DIR/server/requirements.txt"

if [ -f "$REQUIREMENTS" ]; then

    echo
    echo "Installing project dependencies..."
    echo

    python -m pip install -r "$REQUIREMENTS"

else

    echo "ERROR: requirements file not found:"
    echo "$REQUIREMENTS"
    exit 1

fi


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

echo
echo "Creating required directories..."

mkdir -p "$PROJECT_DIR/server/logs"
mkdir -p "$PROJECT_DIR/server/static"
mkdir -p "$PROJECT_DIR/server/templates"


# ============================================================
# MAKE PROJECT SCRIPTS EXECUTABLE
# ============================================================

echo "Setting script permissions..."

find "$PROJECT_DIR/scripts" \
    -type f \
    -name "*.sh" \
    -exec chmod +x {} \;


if [ -f "$PROJECT_DIR/test_server.sh" ]; then
    chmod +x "$PROJECT_DIR/test_server.sh"
fi


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

echo
echo "Initializing database..."

cd "$PROJECT_DIR"

python3 -c "
from server.database.schema import initialize_database
initialize_database()
print('Database initialization successful.')
"


# ============================================================
# PYTHON COMPILE CHECK
# ============================================================

echo
echo "Checking Python source files..."

python3 -m compileall -q "$PROJECT_DIR/server"

echo "Python compilation successful."


# ============================================================
# CHECK NETWORK TOOLS
# ============================================================

echo
echo "Checking network tools..."

if command -v nmcli >/dev/null 2>&1; then
    echo "NetworkManager: available"
else
    echo "WARNING: NetworkManager/nmcli not found."
fi

if command -v iw >/dev/null 2>&1; then
    echo "iw: available"
else
    echo "WARNING: iw not found."
    echo "Wi-Fi AP capability checking will require iw."
fi


# ============================================================
# CHECK FLASK
# ============================================================

echo
echo "Checking Flask..."

if python3 -c "import flask" >/dev/null 2>&1; then

    python3 -c "import flask; print('Flask:', flask.__version__)"

else

    echo "ERROR: Flask installation failed."
    exit 1

fi


# ============================================================
# FINAL MESSAGE
# ============================================================

echo
echo "============================================================"
echo " SERVER SETUP COMPLETE"
echo "============================================================"
echo
echo "Project:"
echo "$PROJECT_DIR"
echo
echo "Virtual environment:"
echo "$VENV_DIR"
echo
echo "Database:"
echo "$PROJECT_DIR/server/database/offline_comm.db"
echo
echo "Next step:"
echo
echo "./scripts/network_check.sh"
echo
echo "After network configuration:"
echo
echo "./scripts/start_server.sh"
echo
echo "============================================================"
echo
