#!/bin/bash

# ============================================================
# OFFLINE COMM SYSTEM
# HP 455 Network Capability Check
# ============================================================

REPORT="network_check_report.txt"

echo "============================================================" > "$REPORT"
echo " OFFLINE COMM SYSTEM" >> "$REPORT"
echo " HP 455 NETWORK CAPABILITY CHECK" >> "$REPORT"
echo "============================================================" >> "$REPORT"
echo >> "$REPORT"

echo "Date:" >> "$REPORT"
date >> "$REPORT"
echo >> "$REPORT"


# ============================================================
# SYSTEM
# ============================================================

echo "============================================================" >> "$REPORT"
echo "SYSTEM INFORMATION" >> "$REPORT"
echo "============================================================" >> "$REPORT"
echo >> "$REPORT"

echo "Hostname:" >> "$REPORT"
hostname >> "$REPORT"
echo >> "$REPORT"

echo "Kernel:" >> "$REPORT"
uname -r >> "$REPORT"
echo >> "$REPORT"


# ============================================================
# NETWORK DEVICES
# ============================================================

echo "============================================================" >> "$REPORT"
echo "NETWORK DEVICES" >> "$REPORT"
echo "============================================================" >> "$REPORT"
echo >> "$REPORT"

if command -v nmcli >/dev/null 2>&1; then
    nmcli device status >> "$REPORT"
else
    echo "nmcli: NOT INSTALLED" >> "$REPORT"
fi

echo >> "$REPORT"


# ============================================================
# WIFI ADAPTER
# ============================================================

echo "============================================================" >> "$REPORT"
echo "WIFI INTERFACES" >> "$REPORT"
echo "============================================================" >> "$REPORT"
echo >> "$REPORT"

if command -v iw >/dev/null 2>&1; then
    iw dev >> "$REPORT"
else
    echo "iw: NOT INSTALLED" >> "$REPORT"
fi

echo >> "$REPORT"


# ============================================================
# WIFI HARDWARE
# ============================================================

echo "============================================================" >> "$REPORT"
echo "WIFI HARDWARE" >> "$REPORT"
echo "============================================================" >> "$REPORT"
echo >> "$REPORT"

if command -v lspci >/dev/null 2>&1; then
    lspci | grep -Ei \
        "network|wireless|wifi|802.11" >> "$REPORT"
fi

echo >> "$REPORT"

if command -v lsusb >/dev/null 2>&1; then
    lsusb | grep -Ei \
        "wireless|wifi|802.11" >> "$REPORT"
fi

echo >> "$REPORT"


# ============================================================
# ACCESS POINT CAPABILITY
# ============================================================

echo "============================================================" >> "$REPORT"
echo "ACCESS POINT CAPABILITY" >> "$REPORT"
echo "============================================================" >> "$REPORT"
echo >> "$REPORT"

if command -v iw >/dev/null 2>&1; then

    WIFI_INTERFACE=$(iw dev | awk '$1=="Interface"{print $2; exit}')

    if [ -n "$WIFI_INTERFACE" ]; then

        echo "Detected Wi-Fi interface:" >> "$REPORT"
        echo "$WIFI_INTERFACE" >> "$REPORT"
        echo >> "$REPORT"

        echo "Supported interface modes:" >> "$REPORT"
        iw phy | grep -A 20 \
            "Supported interface modes" >> "$REPORT"

    else

        echo "No Wi-Fi interface detected." >> "$REPORT"

    fi

else

    echo "Cannot check AP capability because iw is not installed." >> "$REPORT"

fi

echo >> "$REPORT"


# ============================================================
# NETWORK MANAGER
# ============================================================

echo "============================================================" >> "$REPORT"
echo "NETWORK MANAGER" >> "$REPORT"
echo "============================================================" >> "$REPORT"
echo >> "$REPORT"

if command -v nmcli >/dev/null 2>&1; then

    echo "NetworkManager version:" >> "$REPORT"
    nmcli --version >> "$REPORT"

    echo >> "$REPORT"

    echo "Wi-Fi radio:" >> "$REPORT"
    nmcli radio wifi >> "$REPORT"

else

    echo "NetworkManager/nmcli not installed." >> "$REPORT"

fi

echo >> "$REPORT"


# ============================================================
# CURRENT IP ADDRESSES
# ============================================================

echo "============================================================" >> "$REPORT"
echo "CURRENT IP ADDRESSES" >> "$REPORT"
echo "============================================================" >> "$REPORT"
echo >> "$REPORT"

ip -brief address >> "$REPORT"

echo >> "$REPORT"


# ============================================================
# INTERNET / LAN ROUTING
# ============================================================

echo "============================================================" >> "$REPORT"
echo "ROUTING" >> "$REPORT"
echo "============================================================" >> "$REPORT"
echo >> "$REPORT"

ip route >> "$REPORT"

echo >> "$REPORT"


# ============================================================
# SUMMARY
# ============================================================

echo "============================================================" >> "$REPORT"
echo "CHECK COMPLETE" >> "$REPORT"
echo "============================================================" >> "$REPORT"
echo >> "$REPORT"

echo "Report saved as:" >> "$REPORT"
echo "$REPORT" >> "$REPORT"

echo
echo "============================================================"
echo " OFFLINE COMM SYSTEM"
echo " HP 455 NETWORK CHECK COMPLETE"
echo "============================================================"
echo
echo "Report:"
echo "$REPORT"
echo
echo "Run:"
echo
echo "cat $REPORT"
echo
