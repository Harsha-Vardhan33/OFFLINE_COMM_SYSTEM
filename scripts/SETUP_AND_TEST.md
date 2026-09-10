# OFFLINE COMM SYSTEM
# Development Setup and Test Procedure

## 1. Clone the project

git clone <GITHUB_REPOSITORY_URL>

cd OFFLINE_COMM_SYSTEM

## 2. Create Python virtual environment

python3 -m venv venv

## 3. Activate virtual environment

source venv/bin/activate

## 4. Install dependencies

pip install -r server/requirements.txt

## 5. Verify Python files

python -m py_compile \
server/app.py \
server/api/users.py \
server/api/messages.py \
server/api/nodes.py \
server/database/schema.py

## 6. Verify JavaScript files

node --check server/static/js/portal.js
node --check server/static/js/messages.js
node --check server/static/js/dashboard.js

## 7. Start server

python -m server.app

## 8. In another terminal

cd OFFLINE_COMM_SYSTEM
source venv/bin/activate

## 9. Check server

curl -i http://127.0.0.1:5000/

## 10. Check users API

curl -i http://127.0.0.1:5000/api/users

## 11. Check messages API

curl -i http://127.0.0.1:5000/api/messages

## 12. Run automated chat test

python scripts/test_chat_system.py

## 13. LAN test

Replace <LAPTOP_IP> with the laptop Wi-Fi IP:

curl -i http://<LAPTOP_IP>:5000/

curl -i http://<LAPTOP_IP>:5000/api/users

curl -i http://<LAPTOP_IP>:5000/api/messages

## 14. Browser test

Open:

http://<LAPTOP_IP>:5000/

Register:

User A:
Name: Harsha
Node ID: PHONE_001

User B:
Name: Alice
Node ID: PHONE_002

Then verify both users appear and exchange messages.

## Expected final result

Server: PASS
Database: PASS
User registration: PASS
User discovery: PASS
User-to-user messaging: PASS
Conversation retrieval: PASS
LAN access: PASS
