#!/bin/bash

# ============================================================
# OFFLINE COMM SYSTEM
# Wi-Fi Access Point Setup
#
# Purpose:
#   Configure the laptop Wi-Fi adapter as the local
#   OFFLINE_COMM_SYSTEM access point using NetworkManager.
#
# Network:
#   SSID     : OFFLINE_COMM
#   Gateway  : 10.42.0.1
#   DHCP     : NetworkManager shared mode
#   Server   : http://10.42.0.1:5000
#
# Internet is NOT required for the communication system.
# ============================================================

set -e

SSID="OFFLINE_COMM"
PASSWORD="offlineComm@2026"

AP_CONNECTION="OFFLINE_COMM_AP"

AP_IP="10.42.0.1/24"

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"


# ============================================================
# HEADER
# ============================================================

echo
echo "============================================================"
echo " OFFLINE COMM SYSTEM"
echo " WI-FI ACCESS POINT SETUP"
echo "============================================================"
echo


# ============================================================
# ROOT CHECK
# ============================================================

if [ "$EUID" -ne 0 ]; then

    echo "ERROR: This script must be run with sudo."
    echo
    echo "Run:"
    echo
    echo "sudo ./scripts/setup_wifi_ap.sh"
    echo

    exit 1

fi


# ============================================================
# NETWORKMANAGER CHECK
# ============================================================

if ! command -v nmcli >/dev/null 2>&1; then

    echo "ERROR: NetworkManager/nmcli is not installed."
    echo
    echo "Install NetworkManager before continuing."
    exit 1

fi


echo "NetworkManager:"
nmcli --version
echo


# ============================================================
# WIFI RADIO CHECK
# ============================================================

WIFI_STATE=$(nmcli radio wifi)

if [ "$WIFI_STATE" != "enabled" ]; then

    echo "Wi-Fi is disabled."
    echo "Enabling Wi-Fi..."

    nmcli radio wifi on

    sleep 2

fi

echo "Wi-Fi radio: enabled"
echo


# ============================================================
# DETECT WIFI INTERFACE
# ============================================================

WIFI_INTERFACE=$(
    nmcli -t -f DEVICE,TYPE device status |
    awk -F: '$2=="wifi"{print $1; exit}'
)


if [ -z "$WIFI_INTERFACE" ]; then

    echo "ERROR: No Wi-Fi interface detected."
    exit 1

fi


echo "Detected Wi-Fi interface:"
echo "$WIFI_INTERFACE"
echo


# ============================================================
# CHECK AP CAPABILITY
# ============================================================

echo "Checking Wi-Fi AP capability..."

if ! command -v iw >/dev/null 2>&1; then

    echo
    echo "ERROR: 'iw' is not installed."
    echo
    echo "Install it with:"
    echo
    echo "sudo apt install iw"
    echo

    exit 1

fi


PHY=$(
    iw dev "$WIFI_INTERFACE" info 2>/dev/null |
    awk '/wiphy/{print $2; exit}'
)


if [ -z "$PHY" ]; then

    echo "WARNING: Could not determine Wi-Fi PHY."
    echo "NetworkManager will perform the AP capability check."

else

    echo "Wi-Fi PHY:"
    echo "$PHY"
    echo

fi


if iw phy 2>/dev/null |
    sed -n '/Supported interface modes:/,/Band/p' |
    grep -qE '^[[:space:]]*\* AP([[:space:]]|$)'; then

    echo "AP mode: SUPPORTED"

else

    echo
    echo "ERROR: The Wi-Fi adapter does not report AP mode."
    echo
    echo "The built-in Wi-Fi adapter cannot be used as the"
    echo "OFFLINE_COMM_SYSTEM access point with this configuration."
    echo

    exit 1

fi


# ============================================================
# SHOW CURRENT CONNECTION
# ============================================================

echo
echo "Current Wi-Fi connection:"
nmcli -t -f NAME,DEVICE connection show --active || true
echo


# ============================================================
# REMOVE OLD AP PROFILE
# ============================================================

if nmcli connection show "$AP_CONNECTION" >/dev/null 2>&1; then

    echo "Removing existing AP profile..."

    nmcli connection delete "$AP_CONNECTION"

fi


# ============================================================
# CREATE ACCESS POINT
# ============================================================

echo
echo "Creating Wi-Fi access point..."
echo

nmcli connection add \
    type wifi \
    ifname "$WIFI_INTERFACE" \
    con-name "$AP_CONNECTION" \
    autoconnect no \
    ssid "$SSID"


# ============================================================
# CONFIGURE WIFI SECURITY
# ============================================================

nmcli connection modify "$AP_CONNECTION" \
    802-11-wireless.mode ap \
    802-11-wireless.band bg \
    802-11-wireless.channel 6 \
    802-11-wireless-security.key-mgmt wpa-psk \
    802-11-wireless-security.psk "$PASSWORD"


# ============================================================
# CONFIGURE LOCAL NETWORK
# ============================================================

nmcli connection modify "$AP_CONNECTION" \
    ipv4.method shared \
    ipv4.addresses "$AP_IP" \
    ipv6.method disabled


# ============================================================
# START ACCESS POINT
# ============================================================

echo
echo "Starting access point..."
echo

nmcli connection up "$AP_CONNECTION"


# ============================================================
# VERIFY
# ============================================================

echo
echo "============================================================"
echo " ACCESS POINT STATUS"
echo "============================================================"
echo

nmcli connection show "$AP_CONNECTION"


echo
echo "============================================================"
echo " ACTIVE CONNECTIONS"
echo "============================================================"
echo

nmcli device status


# ============================================================
# FINAL INFORMATION
# ============================================================

echo
echo "============================================================"
echo " OFFLINE COMM WI-FI READY"
echo "============================================================"
echo

echo "SSID:"
echo "$SSID"
echo

echo "Password:"
echo "$PASSWORD"
echo

echo "Gateway:"
echo "10.42.0.1"
echo

echo "Flask server:"
echo "http://10.42.0.1:5000"
echo

echo "Captive portal:"
echo "http://10.42.0.1:5000/"
echo

echo "Dashboard:"
echo "http://10.42.0.1:5000/dashboard"
echo

echo "Phone/ESP32 clients should connect to:"
echo "$SSID"
echo

echo "============================================================"
echo
