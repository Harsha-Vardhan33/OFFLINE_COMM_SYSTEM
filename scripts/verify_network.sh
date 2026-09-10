#!/bin/bash

# ============================================================
# OFFLINE COMM SYSTEM
# NETWORK DIAGNOSTIC
# ============================================================

set +e

TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S %z')"
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/network_check.log"

mkdir -p "$LOG_DIR"

exec > >(tee -a "$LOG_FILE") 2>&1


echo
echo "============================================================"
echo " OFFLINE COMM SYSTEM - NETWORK DIAGNOSTIC"
echo "============================================================"
echo "Timestamp : $TIMESTAMP"
echo "Hostname  : $(hostname)"
echo "User      : $(whoami)"
echo "Kernel    : $(uname -r)"
echo "============================================================"


PASS=0
WARN=0
FAIL=0


pass()
{
    echo "[PASS] $1"
    PASS=$((PASS + 1))
}


warn()
{
    echo "[WARN] $1"
    WARN=$((WARN + 1))
}


fail()
{
    echo "[FAIL] $1"
    FAIL=$((FAIL + 1))
}


# ============================================================
# COMMAND CHECK
# ============================================================

echo
echo "------------------------------------------------------------"
echo "COMMANDS"
echo "------------------------------------------------------------"

for CMD in nmcli ip ss curl awk grep systemctl
do
    if command -v "$CMD" >/dev/null 2>&1
    then
        pass "$CMD available"
    else
        fail "$CMD missing"
    fi
done


# ============================================================
# NETWORKMANAGER
# ============================================================

echo
echo "------------------------------------------------------------"
echo "NETWORKMANAGER"
echo "------------------------------------------------------------"

if systemctl is-active --quiet NetworkManager
then
    pass "NetworkManager running"
else
    fail "NetworkManager not running"
fi

echo
nmcli general status


# ============================================================
# DEVICES
# ============================================================

echo
echo "------------------------------------------------------------"
echo "NETWORK DEVICES"
echo "------------------------------------------------------------"

nmcli device status


# ============================================================
# WIFI RADIO
# ============================================================

echo
echo "------------------------------------------------------------"
echo "WIFI RADIO"
echo "------------------------------------------------------------"

nmcli radio wifi


# ============================================================
# OFFLINE COMM PROFILE
# ============================================================

echo
echo "------------------------------------------------------------"
echo "OFFLINE_COMM_AP PROFILE"
echo "------------------------------------------------------------"

AP_NAME="OFFLINE_COMM_AP"

if nmcli connection show "$AP_NAME" >/dev/null 2>&1
then

    pass "OFFLINE_COMM_AP profile exists"

    echo
    nmcli connection show "$AP_NAME"

else

    fail "OFFLINE_COMM_AP profile does not exist"

fi


# ============================================================
# ACTIVE CONNECTION
# ============================================================

echo
echo "------------------------------------------------------------"
echo "ACTIVE CONNECTIONS"
echo "------------------------------------------------------------"

nmcli connection show --active


if nmcli connection show --active | grep -q "$AP_NAME"
then
    pass "OFFLINE_COMM_AP is active"
else
    warn "OFFLINE_COMM_AP is not active"
fi


# ============================================================
# WIFI INTERFACE
# ============================================================

echo
echo "------------------------------------------------------------"
echo "WIFI INTERFACE"
echo "------------------------------------------------------------"

WIFI_INTERFACE="wlo1"

if ip link show "$WIFI_INTERFACE" >/dev/null 2>&1
then

    pass "Wi-Fi interface $WIFI_INTERFACE exists"

    echo
    ip addr show "$WIFI_INTERFACE"

else

    fail "Wi-Fi interface $WIFI_INTERFACE not found"

fi


# ============================================================
# IP ADDRESS
# ============================================================

echo
echo "------------------------------------------------------------"
echo "IP ADDRESSES"
echo "------------------------------------------------------------"

ip -brief address


# ============================================================
# ROUTES
# ============================================================

echo
echo "------------------------------------------------------------"
echo "IPV4 ROUTES"
echo "------------------------------------------------------------"

ip -4 route


# ============================================================
# OFFLINE COMM IP
# ============================================================

echo
echo "------------------------------------------------------------"
echo "OFFLINE_COMM NETWORK"
echo "------------------------------------------------------------"

if ip -4 addr show | grep -q "10.42."
then

    pass "10.42.x.x address exists"

    ip -4 addr show | grep "10.42."

else

    warn "10.42.x.x address does not exist"

fi


# ============================================================
# LINK LOCAL
# ============================================================

echo
echo "------------------------------------------------------------"
echo "DHCP / LINK-LOCAL CHECK"
echo "------------------------------------------------------------"

if ip -4 addr show | grep -q "169.254."
then

    fail "169.254.x.x address detected"

else

    pass "No 169.254.x.x address detected"

fi


# ============================================================
# IP FORWARDING
# ============================================================

echo
echo "------------------------------------------------------------"
echo "IPV4 FORWARDING"
echo "------------------------------------------------------------"

FORWARDING="$(cat /proc/sys/net/ipv4/ip_forward 2>/dev/null)"

echo "net.ipv4.ip_forward = $FORWARDING"

if [ "$FORWARDING" = "1" ]
then

    pass "IPv4 forwarding enabled"

else

    warn "IPv4 forwarding disabled"

fi


# ============================================================
# DHCP / DNS
# ============================================================

echo
echo "------------------------------------------------------------"
echo "DHCP / DNS PORTS"
echo "------------------------------------------------------------"

ss -lunpt 2>/dev/null | grep -E ":(53|67|68)[[:space:]]" || \
    echo "No DHCP/DNS listeners detected"


# ============================================================
# HTTP
# ============================================================

echo
echo "------------------------------------------------------------"
echo "HTTP PORT 80"
echo "------------------------------------------------------------"

if ss -lnt 2>/dev/null | grep -q ":80 "
then
    pass "Port 80 listening"
else
    warn "Port 80 not listening"
fi


# ============================================================
# FLASK
# ============================================================

echo
echo "------------------------------------------------------------"
echo "FLASK PORT 5000"
echo "------------------------------------------------------------"

if ss -lnt 2>/dev/null | grep -q ":5000 "
then

    pass "Port 5000 listening"

else

    fail "Port 5000 not listening"

fi


# ============================================================
# LOCAL FLASK TEST
# ============================================================

echo
echo "------------------------------------------------------------"
echo "LOCAL FLASK TEST"
echo "------------------------------------------------------------"

LOCAL_CODE="$(
    curl \
        --silent \
        --output /dev/null \
        --write-out "%{http_code}" \
        --max-time 5 \
        http://127.0.0.1:5000/
)"

echo "HTTP status: $LOCAL_CODE"

if [ "$LOCAL_CODE" = "200" ]
then

    pass "Local Flask server responding"

else

    fail "Local Flask server not responding"

fi


# ============================================================
# OFFLINE COMM GATEWAY TEST
# ============================================================

echo
echo "------------------------------------------------------------"
echo "OFFLINE_COMM GATEWAY TEST"
echo "------------------------------------------------------------"

if ip -4 addr show | grep -q "10.42.0.1"
then

    GATEWAY_CODE="$(
        curl \
            --silent \
            --output /dev/null \
            --write-out "%{http_code}" \
            --max-time 5 \
            http://10.42.0.1:5000/
    )"

    echo "HTTP status: $GATEWAY_CODE"

    if [ "$GATEWAY_CODE" = "200" ]
    then
        pass "10.42.0.1:5000 responding"
    else
        fail "10.42.0.1:5000 not responding"
    fi

else

    warn "10.42.0.1 is not configured"

fi


# ============================================================
# CAPTIVE PORTAL
# ============================================================

echo
echo "------------------------------------------------------------"
echo "CAPTIVE PORTAL ENDPOINTS"
echo "------------------------------------------------------------"

if ip -4 addr show | grep -q "10.42.0.1"
then

    for PATH_NAME in \
        "/" \
        "/generate_204" \
        "/hotspot-detect.html" \
        "/connecttest.txt" \
        "/ncsi.txt"
    do

        CODE="$(
            curl \
                --silent \
                --output /dev/null \
                --write-out "%{http_code}" \
                --max-time 5 \
                "http://10.42.0.1:5000$PATH_NAME"
        )"

        echo "$PATH_NAME -> HTTP $CODE"

    done

else

    echo "Skipped: OFFLINE_COMM network is not active."

fi


# ============================================================
# LISTENING SERVICES
# ============================================================

echo
echo "------------------------------------------------------------"
echo "LISTENING SERVICES"
echo "------------------------------------------------------------"

ss -lntup 2>/dev/null


# ============================================================
# SERVER PROCESS
# ============================================================

echo
echo "------------------------------------------------------------"
echo "FLASK PROCESS"
echo "------------------------------------------------------------"

ps aux | grep "[p]ython.*server"


# ============================================================
# SYSTEM LOAD
# ============================================================

echo
echo "------------------------------------------------------------"
echo "SYSTEM RESOURCES"
echo "------------------------------------------------------------"

echo
echo "Uptime:"
uptime

echo
echo "Memory:"
free -h

echo
echo "Disk:"
df -h .


# ============================================================
# SUMMARY
# ============================================================

echo
echo "============================================================"
echo "SUMMARY"
echo "============================================================"

echo "PASS : $PASS"
echo "WARN : $WARN"
echo "FAIL : $FAIL"
echo
echo "Timestamp : $TIMESTAMP"
echo "Log file  : $LOG_FILE"


if [ "$FAIL" -eq 0 ]
then

    echo
    echo "============================================================"
    echo " RESULT: PASS"
    echo "============================================================"

    exit 0

else

    echo
    echo "============================================================"
    echo " RESULT: FAIL"
    echo "============================================================"

    exit 1

fi
