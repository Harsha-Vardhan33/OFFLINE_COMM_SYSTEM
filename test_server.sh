#!/bin/bash

# ============================================================
# OFFLINE COMM SYSTEM
# Server API Test Suite
# ============================================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPORT_FILE="$PROJECT_DIR/server_test_report.txt"

BASE_URL="http://127.0.0.1:5000"

PASS_COUNT=0
FAIL_COUNT=0


# ============================================================
# REPORT HEADER
# ============================================================

{
    echo "============================================================"
    echo " OFFLINE COMM SYSTEM"
    echo " SERVER API TEST REPORT"
    echo "============================================================"
    echo
    echo "Date:"
    date
    echo
    echo "Server:"
    echo "$BASE_URL"
    echo
    echo "============================================================"
    echo
} > "$REPORT_FILE"


# ============================================================
# TEST FUNCTION
# ============================================================

run_test()
{
    TEST_NAME="$1"
    METHOD="$2"
    URL="$3"
    DATA="$4"

    echo "Running: $TEST_NAME"

    {
        echo "------------------------------------------------------------"
        echo "TEST: $TEST_NAME"
        echo "------------------------------------------------------------"
        echo
        echo "REQUEST:"
        echo "$METHOD $URL"

        if [ -n "$DATA" ]; then
            echo
            echo "DATA:"
            echo "$DATA"
        fi

        echo
        echo "RESPONSE:"
    } >> "$REPORT_FILE"


    TEMP_BODY=$(mktemp)


    if [ "$METHOD" = "GET" ]; then

        HTTP_CODE=$(curl \
            -sS \
            -o "$TEMP_BODY" \
            -w "%{http_code}" \
            "$URL")

    else

        HTTP_CODE=$(curl \
            -sS \
            -o "$TEMP_BODY" \
            -w "%{http_code}" \
            -X "$METHOD" \
            -H "Content-Type: application/json" \
            -d "$DATA" \
            "$URL")

    fi


    CURL_EXIT=$?


    cat "$TEMP_BODY" >> "$REPORT_FILE"


    {
        echo
        echo
        echo "HTTP STATUS: $HTTP_CODE"
        echo "CURL EXIT CODE: $CURL_EXIT"
    } >> "$REPORT_FILE"


    if [ "$CURL_EXIT" -eq 0 ] &&
       [ "$HTTP_CODE" -ge 200 ] &&
       [ "$HTTP_CODE" -lt 300 ]; then

        echo "RESULT: PASS" >> "$REPORT_FILE"

        PASS_COUNT=$((PASS_COUNT + 1))

    else

        echo "RESULT: FAIL" >> "$REPORT_FILE"

        FAIL_COUNT=$((FAIL_COUNT + 1))

    fi


    echo >> "$REPORT_FILE"


    rm -f "$TEMP_BODY"
}


# ============================================================
# BASIC SERVER TESTS
# ============================================================

run_test \
"Root endpoint" \
"GET" \
"$BASE_URL/" \
""


run_test \
"Health endpoint" \
"GET" \
"$BASE_URL/api/health" \
""


run_test \
"System status endpoint" \
"GET" \
"$BASE_URL/api/status" \
""


# ============================================================
# INITIAL GET TESTS
# ============================================================

run_test \
"GET nodes" \
"GET" \
"$BASE_URL/api/nodes" \
""


run_test \
"GET SOS alerts" \
"GET" \
"$BASE_URL/api/sos" \
""


run_test \
"GET messages" \
"GET" \
"$BASE_URL/api/messages" \
""


run_test \
"GET locations" \
"GET" \
"$BASE_URL/api/locations" \
""


run_test \
"GET resources" \
"GET" \
"$BASE_URL/api/resources" \
""


# ============================================================
# NODE API
# ============================================================

NODE_DATA='{
    "node_id": "TEST_NODE_01",
    "node_name": "Test Node",
    "ip_address": "192.168.4.10",
    "role": "NODE",
    "status": "ONLINE",
    "battery": 95,
    "signal_strength": -42
}'


run_test \
"POST node registration" \
"POST" \
"$BASE_URL/api/nodes" \
"$NODE_DATA"


run_test \
"GET nodes after registration" \
"GET" \
"$BASE_URL/api/nodes" \
""


# ============================================================
# SOS API
# ============================================================

SOS_DATA='{
    "node_id": "TEST_NODE_01",
    "user_name": "TEST_USER",
    "message": "Automated server test SOS",
    "latitude": 11.0168,
    "longitude": 76.9558,
    "priority": "HIGH"
}'


run_test \
"POST SOS alert" \
"POST" \
"$BASE_URL/api/sos" \
"$SOS_DATA"


run_test \
"GET SOS after creation" \
"GET" \
"$BASE_URL/api/sos" \
""


# ============================================================
# MESSAGE API
# ============================================================

MESSAGE_DATA='{
    "node_id": "TEST_NODE_01",
    "sender": "TEST_USER",
    "receiver": "RESCUE",
    "message": "Automated server test message",
    "message_type": "TEXT"
}'


run_test \
"POST message" \
"POST" \
"$BASE_URL/api/messages" \
"$MESSAGE_DATA"


run_test \
"GET messages after creation" \
"GET" \
"$BASE_URL/api/messages" \
""


# ============================================================
# LOCATION API
# ============================================================

LOCATION_DATA='{
    "node_id": "TEST_NODE_01",
    "user_name": "TEST_USER",
    "latitude": 11.0168,
    "longitude": 76.9558,
    "accuracy": 5
}'


run_test \
"POST location" \
"POST" \
"$BASE_URL/api/locations" \
"$LOCATION_DATA"


run_test \
"GET locations after creation" \
"GET" \
"$BASE_URL/api/locations" \
""


# ============================================================
# RESOURCE API
# ============================================================

RESOURCE_DATA='{
    "node_id": "TEST_NODE_01",
    "user_name": "TEST_USER",
    "resource": "WATER",
    "quantity": 10,
    "priority": "HIGH"
}'


run_test \
"POST resource request" \
"POST" \
"$BASE_URL/api/resources" \
"$RESOURCE_DATA"


run_test \
"GET resources after creation" \
"GET" \
"$BASE_URL/api/resources" \
""


# ============================================================
# FINAL STATUS
# ============================================================

run_test \
"Final system status" \
"GET" \
"$BASE_URL/api/status" \
""


# ============================================================
# LAN TEST
# ============================================================

LAN_IP=$(hostname -I | awk '{print $1}')


if [ -n "$LAN_IP" ]; then

    run_test \
    "LAN health endpoint" \
    "GET" \
    "http://$LAN_IP:5000/api/health" \
    ""

else

    {
        echo "------------------------------------------------------------"
        echo "TEST: LAN health endpoint"
        echo "------------------------------------------------------------"
        echo
        echo "LAN IP could not be determined."
        echo
        echo "RESULT: SKIPPED"
        echo
    } >> "$REPORT_FILE"

fi


# ============================================================
# SUMMARY
# ============================================================

TOTAL_COUNT=$((PASS_COUNT + FAIL_COUNT))


{
    echo "============================================================"
    echo " TEST SUMMARY"
    echo "============================================================"
    echo
    echo "TOTAL TESTS : $TOTAL_COUNT"
    echo "PASSED      : $PASS_COUNT"
    echo "FAILED      : $FAIL_COUNT"
    echo
} >> "$REPORT_FILE"


if [ "$FAIL_COUNT" -eq 0 ]; then

    echo "OVERALL RESULT: PASS" >> "$REPORT_FILE"

else

    echo "OVERALL RESULT: FAIL" >> "$REPORT_FILE"

fi


{
    echo
    echo "Completed:"
    date
    echo
    echo "============================================================"
} >> "$REPORT_FILE"


# ============================================================
# TERMINAL SUMMARY
# ============================================================

echo
echo "============================================================"
echo " OFFLINE COMM SYSTEM SERVER TEST"
echo "============================================================"
echo
echo "Total : $TOTAL_COUNT"
echo "Passed: $PASS_COUNT"
echo "Failed: $FAIL_COUNT"
echo
echo "Report:"
echo "$REPORT_FILE"
echo

if [ "$FAIL_COUNT" -eq 0 ]; then

    echo "OVERALL RESULT: PASS"

else

    echo "OVERALL RESULT: FAIL"

fi

echo
