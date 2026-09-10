#!/usr/bin/env python3
"""
OFFLINE COMM SYSTEM
Final Chat System Integration Test

Checks:
1. Server connectivity
2. User registration
3. Registered users appear in /api/users
4. User A -> User B message
5. User B -> User A message
6. Private conversation retrieval
7. SQLite persistence
8. Cleanup of temporary test data

No frontend files are modified.
No frontend features are added.

Usage:
    python scripts/test_chat_system.py

LAN server:
    python scripts/test_chat_system.py http://10.213.244.207:5000
"""

from __future__ import annotations

import json
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_BASE_URL = "http://127.0.0.1:5000"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "server" / "database" / "offline_comm.db"

TEST_USER_A = "CHAT_TEST_A"
TEST_USER_B = "CHAT_TEST_B"

TEST_NODE_A = "TEST_CHAT_NODE_A"
TEST_NODE_B = "TEST_CHAT_NODE_B"

MESSAGE_A_TO_B = "CHAT_SYSTEM_TEST_A_TO_B"
MESSAGE_B_TO_A = "CHAT_SYSTEM_TEST_B_TO_A"


class TestFailure(Exception):
    pass


def header(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def request_json(
    base_url: str,
    path: str,
    method: str = "GET",
    payload=None,
):
    url = base_url.rstrip("/") + path

    body = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            raw = response.read().decode("utf-8")
            content_type = response.headers.get("Content-Type", "")

            if "application/json" in content_type:
                data = json.loads(raw) if raw else None
            else:
                data = raw

            return response.status, data

    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")

        try:
            data = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            data = raw

        return error.code, data

    except urllib.error.URLError as error:
        raise TestFailure(
            f"Cannot connect to {url}\n"
            f"Reason: {error.reason}"
        ) from error


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TestFailure(message)


def user_exists(users, name: str) -> bool:
    if not isinstance(users, list):
        return False

    for user in users:
        if not isinstance(user, dict):
            continue

        actual_name = (
            user.get("user_name")
            or user.get("name")
            or user.get("username")
            or ""
        )

        if str(actual_name).strip() == name:
            return True

    return False


def conversation_contains(
    conversation,
    sender: str,
    receiver: str,
    text: str,
) -> bool:
    if not isinstance(conversation, list):
        return False

    for message in conversation:
        if not isinstance(message, dict):
            continue

        if (
            message.get("sender") == sender
            and message.get("receiver") == receiver
            and message.get("message") == text
        ):
            return True

    return False


def cleanup_database() -> None:
    """Remove only this script's temporary test records."""

    if not DATABASE_PATH.exists():
        return

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute(
            """
            DELETE FROM messages
            WHERE
                (sender = ? AND receiver = ?)
                OR
                (sender = ? AND receiver = ?)
            """,
            (
                TEST_USER_A,
                TEST_USER_B,
                TEST_USER_B,
                TEST_USER_A,
            ),
        )

        connection.execute(
            """
            DELETE FROM users
            WHERE user_name IN (?, ?)
            """,
            (
                TEST_USER_A,
                TEST_USER_B,
            ),
        )

        connection.commit()

    finally:
        connection.close()


def main() -> int:
    base_url = (
        sys.argv[1].rstrip("/")
        if len(sys.argv) > 1
        else DEFAULT_BASE_URL
    )

    header("OFFLINE COMM SYSTEM - FINAL CHAT SYSTEM TEST")

    print(f"Server   : {base_url}")
    print(f"Database : {DATABASE_PATH}")
    print()
    print("Temporary users/messages will be created.")
    print("They will be removed automatically.")
    print("Frontend files will NOT be modified.")

    # Remove leftovers if a previous run was interrupted.
    cleanup_database()

    try:
        # ------------------------------------------------------------
        # 1. SERVER
        # ------------------------------------------------------------

        header("1. SERVER CONNECTIVITY")

        status, response = request_json(
            base_url,
            "/api/users",
        )

        require(
            status == 200,
            f"GET /api/users failed: HTTP {status} -> {response}",
        )

        print("[PASS] Server is reachable.")
        print("[PASS] GET /api/users -> HTTP 200.")

        # ------------------------------------------------------------
        # 2. REGISTER USER A
        # ------------------------------------------------------------

        header("2. REGISTER USER A")

        status, response = request_json(
            base_url,
            "/api/users",
            "POST",
            {
                "user_name": TEST_USER_A,
                "node_id": TEST_NODE_A,
            },
        )

        require(
            status == 201,
            f"User A registration failed: HTTP {status} -> {response}",
        )

        print(f"[PASS] {TEST_USER_A} registered.")

        # ------------------------------------------------------------
        # 3. REGISTER USER B
        # ------------------------------------------------------------

        header("3. REGISTER USER B")

        status, response = request_json(
            base_url,
            "/api/users",
            "POST",
            {
                "user_name": TEST_USER_B,
                "node_id": TEST_NODE_B,
            },
        )

        require(
            status == 201,
            f"User B registration failed: HTTP {status} -> {response}",
        )

        print(f"[PASS] {TEST_USER_B} registered.")

        # ------------------------------------------------------------
        # 4. VERIFY USERS APPEAR
        # ------------------------------------------------------------

        header("4. VERIFY USERS APPEAR IN USER LIST")

        status, users = request_json(
            base_url,
            "/api/users",
        )

        require(
            status == 200,
            f"GET /api/users failed: HTTP {status} -> {users}",
        )

        require(
            user_exists(users, TEST_USER_A),
            f"{TEST_USER_A} does not appear in /api/users.",
        )

        require(
            user_exists(users, TEST_USER_B),
            f"{TEST_USER_B} does not appear in /api/users.",
        )

        print(f"[PASS] {TEST_USER_A} appears in user list.")
        print(f"[PASS] {TEST_USER_B} appears in user list.")

        # ------------------------------------------------------------
        # 5. A -> B
        # ------------------------------------------------------------

        header("5. USER A -> USER B")

        status, response = request_json(
            base_url,
            "/api/messages",
            "POST",
            {
                "node_id": TEST_NODE_A,
                "sender": TEST_USER_A,
                "receiver": TEST_USER_B,
                "message": MESSAGE_A_TO_B,
                "message_type": "TEXT",
            },
        )

        require(
            status == 201,
            f"A -> B message failed: HTTP {status} -> {response}",
        )

        print("[PASS] A -> B message accepted with HTTP 201.")

        # ------------------------------------------------------------
        # 6. B -> A
        # ------------------------------------------------------------

        header("6. USER B -> USER A")

        status, response = request_json(
            base_url,
            "/api/messages",
            "POST",
            {
                "node_id": TEST_NODE_B,
                "sender": TEST_USER_B,
                "receiver": TEST_USER_A,
                "message": MESSAGE_B_TO_A,
                "message_type": "TEXT",
            },
        )

        require(
            status == 201,
            f"B -> A message failed: HTTP {status} -> {response}",
        )

        print("[PASS] B -> A message accepted with HTTP 201.")

        # ------------------------------------------------------------
        # 7. CONVERSATION
        # ------------------------------------------------------------

        header("7. VERIFY PRIVATE CONVERSATION")

        query = urllib.parse.urlencode(
            {
                "sender": TEST_USER_A,
                "receiver": TEST_USER_B,
            }
        )

        status, conversation = request_json(
            base_url,
            f"/api/messages/conversation?{query}",
        )

        require(
            status == 200,
            f"Conversation request failed: HTTP {status} -> {conversation}",
        )

        require(
            conversation_contains(
                conversation,
                TEST_USER_A,
                TEST_USER_B,
                MESSAGE_A_TO_B,
            ),
            "A -> B message is missing from the conversation.",
        )

        require(
            conversation_contains(
                conversation,
                TEST_USER_B,
                TEST_USER_A,
                MESSAGE_B_TO_A,
            ),
            "B -> A message is missing from the conversation.",
        )

        print("[PASS] A -> B message retrieved.")
        print("[PASS] B -> A message retrieved.")

        # ------------------------------------------------------------
        # 8. SQLITE
        # ------------------------------------------------------------

        header("8. VERIFY SQLITE PERSISTENCE")

        require(
            DATABASE_PATH.exists(),
            f"Database does not exist: {DATABASE_PATH}",
        )

        connection = sqlite3.connect(DATABASE_PATH)

        try:
            user_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM users
                WHERE user_name IN (?, ?)
                """,
                (
                    TEST_USER_A,
                    TEST_USER_B,
                ),
            ).fetchone()[0]

            message_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE
                    (sender = ? AND receiver = ?)
                    OR
                    (sender = ? AND receiver = ?)
                """,
                (
                    TEST_USER_A,
                    TEST_USER_B,
                    TEST_USER_B,
                    TEST_USER_A,
                ),
            ).fetchone()[0]

        finally:
            connection.close()

        require(
            user_count == 2,
            f"Expected 2 test users in SQLite, found {user_count}.",
        )

        require(
            message_count == 2,
            f"Expected 2 test messages in SQLite, found {message_count}.",
        )

        print("[PASS] Both users persisted in SQLite.")
        print("[PASS] Both messages persisted in SQLite.")

        # ------------------------------------------------------------
        # 9. CLEANUP
        # ------------------------------------------------------------

        header("9. CLEANUP")

        cleanup_database()

        status, users_after_cleanup = request_json(
            base_url,
            "/api/users",
        )

        require(
            status == 200,
            "Could not verify cleanup.",
        )

        require(
            not user_exists(users_after_cleanup, TEST_USER_A),
            f"{TEST_USER_A} still exists after cleanup.",
        )

        require(
            not user_exists(users_after_cleanup, TEST_USER_B),
            f"{TEST_USER_B} still exists after cleanup.",
        )

        print("[PASS] Temporary users removed.")
        print("[PASS] Temporary messages removed.")

        # ------------------------------------------------------------
        # FINAL
        # ------------------------------------------------------------

        header("FINAL RESULT")

        print("CHAT SYSTEM TEST: PASS")
        print()
        print("Verified:")
        print("  [PASS] Server connectivity")
        print("  [PASS] User registration")
        print("  [PASS] Users appear in network list")
        print("  [PASS] User A -> User B")
        print("  [PASS] User B -> User A")
        print("  [PASS] Private conversation retrieval")
        print("  [PASS] SQLite persistence")
        print("  [PASS] Test-data cleanup")
        print()
        print("Basic chat backend/API flow is READY.")
        print("Proceed to final browser test before Git commit/push.")

        return 0

    except TestFailure as error:
        header("FINAL RESULT")
        print("CHAT SYSTEM TEST: FAIL")
        print()
        print(error)
        return 1

    except Exception as error:
        header("FINAL RESULT")
        print("CHAT SYSTEM TEST: FAIL")
        print()
        print(f"Unexpected error: {type(error).__name__}: {error}")
        return 1

    finally:
        try:
            cleanup_database()
        except Exception as cleanup_error:
            print(f"WARNING: automatic cleanup failed: {cleanup_error}")


if __name__ == "__main__":
    raise SystemExit(main())
