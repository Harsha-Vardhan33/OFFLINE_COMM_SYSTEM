# OFFLINE COMMUNICATION SYSTEM

## Mesh-Based Offline Emergency Communication and Rescue Coordination System Using ESP32

An offline communication prototype designed to provide local communication and data exchange when conventional Internet/cellular connectivity is unavailable.

The system uses **ESP32 nodes**, **SX1278 LoRa transceivers**, a **local Flask server**, and **Wi-Fi** to bridge user devices with a long-range LoRa communication link.

> **Current project status:** The core local server, Wi-Fi access, ESP32 gateway communication, LoRa packet/data transfer, and webpage/data transmission have been developed and tested. **Voice communication over LoRa is still experimental and is currently not functioning correctly; it is intentionally left as an open integration task for further development.**

---

## 1. Project Overview

During disasters such as floods, cyclones, earthquakes, landslides, and storms, cellular networks and Internet infrastructure may become unavailable.

This project investigates an offline communication architecture in which:

- A laptop provides the local application/server infrastructure.
- ESP32 hardware acts as the communication gateway.
- SX1278 LoRa modules provide long-range wireless packet transport.
- Nearby smartphones/clients communicate with the system through Wi-Fi and a web browser.
- Application data can be transferred through the LoRa link without requiring Internet access.

The project is intended as an academic prototype for **offline emergency communication and rescue coordination**.

---

## 2. Current Architecture

The currently developed architecture is centered around a local laptop/Flask server and ESP32-LoRa gateways.

```text
                         LOCAL / CENTRAL NODE
                    ┌───────────────────────────┐
                    │        Old Laptop         │
                    │                           │
                    │  Flask Application        │
                    │  Local Database            │
                    │  Web Dashboard             │
                    │  Local Wi-Fi Access Point  │
                    └─────────────┬─────────────┘
                                  │
                              USB / Serial
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      ESP32 Gateway         │
                    │                           │
                    │  Wi-Fi ↔ Serial ↔ LoRa   │
                    └─────────────┬─────────────┘
                                  │
                              SX1278 LoRa
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │    Remote ESP32 Node       │
                    │                           │
                    │       LoRa ↔ Wi-Fi        │
                    └─────────────┬─────────────┘
                                  │
                               Wi-Fi
                                  │
                                  ▼
                         Smartphone / Client
                           Web Interface
```

### Important architecture note

The laptop remains the **central application/server node**. The ESP32 is used as the communication gateway between the laptop/server side and the LoRa link.

The remote communication path is therefore not dependent on an Internet connection.

---

## 3. Main Technologies

| Layer | Technology |
|---|---|
| Microcontroller | ESP32 |
| Long-range radio | SX1278 LoRa |
| Local wireless access | Wi-Fi |
| Server | Python + Flask |
| Serial communication | USB / PySerial |
| Frontend | HTML / CSS / JavaScript |
| Local database | SQLite |
| Embedded development | Arduino / PlatformIO |
| Server port | `5000` |
| Communication model | Wi-Fi ↔ ESP32 ↔ LoRa ↔ ESP32 ↔ Wi-Fi |

---

## 4. Repository Structure

The current public GitHub repository contains these top-level project items:

```text
OFFLINE_COMM_SYSTEM/
│
├── esp32/
│   └── gateway/
│
├── scripts/
│
├── server/
│
├── .gitignore
├── README.md
├── network_check.sh
├── requirements.txt
└── test_server.sh
```

The main implementation areas are:

```text
esp32/gateway/
    └── ESP32 gateway firmware

server/
    └── Flask application, APIs, web interface and server-side services

scripts/
    └── Network/setup utilities

network_check.sh
    └── Network verification utility

test_server.sh
    └── Server testing utility

requirements.txt
    └── Python dependencies
```

The repository is maintained on the `main` branch.

## 5. Implemented Components

### 5.1 Local Flask Server

The project includes a Flask-based local server.

The server is designed to:

- Serve the browser interface.
- Provide local REST APIs.
- Store communication/application data locally.
- Communicate with the ESP32 gateway through serial communication.
- Operate without requiring cloud infrastructure.

The server runs on:

```text
0.0.0.0:5000
```

Example local access from the server itself:

```text
http://127.0.0.1:5000
```

### Currently verified LAN address

The latest repository/runtime record shows the Flask server running on:

```text
http://10.143.160.207:5000
```

Main web interface:

```text
http://10.143.160.207:5000/
```

Messaging interface:

```text
http://10.143.160.207:5000/messages
```

The server is bound to:

```text
0.0.0.0:5000
```

**Important:** `10.143.160.207` is a LAN address and may change when the laptop reconnects to a different Wi-Fi network or receives a different DHCP lease. If it changes, use the laptop's current LAN IP with port `5000`.

To check the current address on Linux:

```bash
hostname -I
```

or:

```bash
ip addr
```

Then access:

```text
http://<CURRENT-LAN-IP>:5000
```

---

### 5.2 Local Wi-Fi Access Point

A Wi-Fi access-point setup script is included for creating the local offline network.

The local Wi-Fi network allows:

```text
Smartphone
    │
    │ Wi-Fi
    ▼
Old Laptop
    │
    │ Flask
    ▼
Web Interface
```

No Internet connection is required for the local application itself.

The project includes:

```text
scripts/setup_wifi_ap.sh
```

The script configures the Linux machine as the local Wi-Fi access point and assigns the local network configuration.

---

### 5.3 ESP32 Gateway

The ESP32 gateway firmware is located at:

```text
esp32/gateway/gateway.ino
```

The gateway provides the hardware-side bridge between:

```text
Laptop / Flask
        ↕
     USB Serial
        ↕
      ESP32
        ↕
      SX1278
        ↕
       LoRa
```

The gateway has been tested for serial communication with the server-side system.

The gateway identifies itself using:

```text
ESP32-GW-01
```

and reports a ready state during startup.

---

### 5.4 Serial Communication

The Linux laptop communicates with the ESP32 using USB serial.

The development/test environment used:

```text
/dev/ttyUSB0
```

PySerial is used for serial communication.

The server-side gateway service is located under:

```text
server/services/esp32_gateway.py
```

Basic ESP32 communication endpoints have been tested, including:

```text
/api/esp32/ping
/api/esp32/id
/api/esp32/status
```

Example successful responses included:

```text
PONG
```

and:

```text
NODE_ID|ESP32-GW-01
```

---

## 6. LoRa Communication

The project uses **SX1278 LoRa modules** for long-range packet communication.

The LoRa link is intended to provide communication between ESP32 nodes without depending on cellular or Internet connectivity.

The development work has included:

- LoRa packet transmission.
- LoRa packet reception.
- ESP32-to-ESP32 communication.
- Bridging application data between the laptop/server side and the LoRa side.
- Testing of transferred webpage/data content over the communication path.

### Current status

**Packet/data communication is functioning sufficiently for the current prototype.**

The remaining major problem is the **voice packet/call subsystem**, described below.

---

## 7. Webpage / Data Transmission

The system was developed to transfer application/web data through the communication chain rather than creating an independent Internet-based server at the remote node.

The intended data path is:

```text
Laptop Flask Server
        │
        ▼
      ESP32
        │
        ▼
    SX1278 LoRa
        │
        ▼
Remote ESP32
        │
        ▼
      Wi-Fi
        │
        ▼
 Smartphone / Browser
```

The project has reached the stage where packet/data transfer through the LoRa communication path can be tested.

This part of the system is separate from the unfinished voice subsystem.

---

## 8. Browser-Based Communication

The project uses a browser-based interface so that a client device does not need a dedicated mobile application for the prototype.

The server contains web pages including:

```text
/dashboard
/messages
```

and supporting frontend assets under:

```text
server/templates/
server/static/
```

The messaging interface is intended to support offline/local communication through the project network.

---

## 9. Voice Communication — Current Limitation

### Status: NOT COMPLETED

Voice communication was added as an experimental extension to the system.

The intended architecture is:

```text
Phone Microphone
       │
       ▼
      Wi-Fi
       │
       ▼
     ESP32
       │
       ▼
   SX1278 LoRa
       │
       ▼
     ESP32
       │
       ▼
      Wi-Fi
       │
       ▼
Phone Speaker
```

However, the **voice packet transmission/reception is currently not functioning correctly**.

The voice subsystem should therefore be treated as:

```text
EXPERIMENTAL / WORK IN PROGRESS
```

It has **not** been represented as a completed feature in this repository.

### Handoff objective

Further development is required to investigate:

- Audio packetization.
- Packet fragmentation and reassembly.
- Packet ordering.
- Buffering.
- Timing and latency.
- Packet loss handling.
- Audio encoding/compression.
- LoRa payload limitations.
- Synchronization between transmitter and receiver.
- Reliable playback on the receiving device.

The repository is being provided to a project development center for further investigation and implementation of this subsystem.

---

## 10. Database

The Flask application uses a local database for offline operation.

The project has database structures for application data including communication-related information and emergency-response data.

The system is designed to avoid dependence on an external cloud database during offline operation.

---

## 11. Offline Operation

A major design objective is to keep the communication infrastructure operational without Internet connectivity.

The system separates:

```text
Internet
   X
   │
   │ not required
   ▼
Local Wi-Fi + Flask + ESP32 + LoRa
```

The local application can operate within the deployed communication network.

---

## 12. Setup

### 12.1 Clone the repository

```bash
git clone https://github.com/Harsha-Vardhan33/OFFLINE_COMM_SYSTEM.git
cd OFFLINE_COMM_SYSTEM
```

### 12.2 Create a Python virtual environment

Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 12.3 Install Python dependencies

```bash
pip install -r requirements.txt
```

### 12.4 Start the Flask server

From the repository root:

```bash
python -m server.app
```

The server listens on:

```text
http://127.0.0.1:5000
```

For access from devices on the local network:

```text
http://<SERVER-IP>:5000
```

---

## 13. ESP32 Setup

Open:

```text
esp32/gateway/gateway.ino
```

using Arduino IDE or the configured embedded development environment.

Configure the ESP32 board and upload the gateway firmware.

After connecting the ESP32 through USB, identify the serial device on Linux:

```bash
ls /dev/ttyUSB*
```

The development setup has used:

```text
/dev/ttyUSB0
```

The exact device name may differ depending on the operating system and USB device enumeration.

---

## 14. Basic Server Verification

After starting the Flask server, test the local server:

```bash
curl http://127.0.0.1:5000/
```

Test the ESP32 gateway API:

```bash
curl http://127.0.0.1:5000/api/esp32/ping
```

Expected response:

```text
PONG
```

Test the gateway identity:

```bash
curl http://127.0.0.1:5000/api/esp32/id
```

Expected format:

```text
NODE_ID|ESP32-GW-01
```

Additional server tests are available in:

```text
test_server.sh
network_check.sh
```

---

## 15. Development Workflow

The project was developed using the following workflow:

```text
Victus Laptop
    │
    │ Develop / test
    ▼
GitHub Repository
    │
    │ Pull latest project
    ▼
Old Laptop
    │
    ├── Flask Server
    ├── Local Wi-Fi
    └── USB → ESP32 Gateway
             │
             ▼
          LoRa Link
```

The **Victus laptop** is the primary development machine.

The **old laptop** is used as the deployment/server machine.

---

## 16. Current Project Status

| Component | Status |
|---|---|
| Flask local server | ✅ Implemented |
| Local offline Wi-Fi network | ✅ Implemented |
| Browser-based interface | ✅ Implemented |
| ESP32 gateway firmware | ✅ Implemented |
| USB serial communication | ✅ Tested |
| ESP32 identification/status APIs | ✅ Tested |
| SX1278 LoRa packet transmission | ✅ Implemented/Tested |
| SX1278 LoRa packet reception | ✅ Implemented/Tested |
| Laptop ↔ ESP32 ↔ LoRa data path | ✅ Tested |
| Web/data transfer over communication path | ✅ Developed/Tested |
| Local message interface | ✅ Implemented |
| Offline/local database | ✅ Implemented |
| Voice packet transmission | ⚠️ Experimental |
| Voice packet reception/playback | ⚠️ Not functioning correctly |
| Reliable real-time voice call | ❌ Not completed |
| Full final system validation | 🔄 Ongoing |

---

## 17. Known Limitations

The current prototype has the following known limitations:

1. Voice communication over the LoRa link is not yet functioning correctly.
2. The voice subsystem requires further packetization, buffering, synchronization, and reliability work.
3. LoRa bandwidth and payload constraints must be considered when designing the voice protocol.
4. The current implementation is a research/academic prototype and has not been validated as a production emergency-communication system.
5. Range, throughput, latency, packet-loss rate, and multi-node performance require systematic field testing.

---

## 18. Intended Applications

The project is intended to investigate applications such as:

- Disaster communication.
- Emergency messaging.
- SOS alert transmission.
- Rescue coordination.
- Remote/off-grid communication.
- Local information exchange when conventional networks are unavailable.

Potential users include:

- Disaster-response teams.
- Rescue organizations.
- Local administrations.
- NGOs.
- Remote/off-grid communities.

---

## 19. Academic Project Information

**Project Title**

> MESH-BASED OFFLINE EMERGENCY COMMUNICATION AND RESCUE COORDINATION SYSTEM USING ESP32 FOR DISASTER MANAGEMENT

**Project Work:** Phase I — Project Work (23EC701)

**Department:** Electronics and Communication Engineering

**Institution:** Sri Krishna College of Engineering & Technology, Coimbatore

**Batch:** 6

### Project Members

- **Harsha Vardhan T** — 727723EUEC501
- **Ajay Athish S A** — 727723EUEC011
- **Aswin Aadhithya M** — 727724EUEC501

---

## 20. Development Handoff

This repository is intended to serve as the current source for continued development.

### Working baseline

The following should be considered the current working baseline:

```text
Flask server
    +
Local Wi-Fi
    +
ESP32 gateway
    +
USB serial
    +
SX1278 LoRa packet communication
    +
Browser/data transfer
```

### Primary unfinished task

The primary unfinished subsystem is:

```text
VOICE COMMUNICATION OVER LORA
```

Future developers should first reproduce the existing working packet/data communication path before modifying the voice subsystem.

This makes it possible to distinguish a regression in the established communication path from a problem specifically introduced by the voice implementation.

---

## 21. Handoff to Further Development

This repository is being provided to a project development center for continued technical work.

The current working baseline is:

```text
Local Flask Server
        │
        ▼
      USB/Serial
        │
        ▼
    ESP32 Gateway
        │
        ▼
     SX1278 LoRa
        │
        ▼
   Remote ESP32
        │
        ▼
      Wi-Fi
        │
        ▼
   Browser / Client
```

### Already developed/tested

- Flask server and local web interface.
- Local Wi-Fi access.
- ESP32 gateway communication.
- USB/serial communication.
- LoRa packet transmission and reception.
- Application/data transfer through the communication path.

### Remaining development focus

The main unfinished subsystem is:

```text
VOICE COMMUNICATION OVER LORA
```

Voice packet transmission/reception and reliable real-time voice communication are **not claimed as completed features** in this repository.

Further work should begin by reproducing the existing packet/data communication path and then isolating the voice subsystem.

## 22. Security and Repository Notes

This project is intended for academic development and testing.

Before deploying the repository publicly, ensure that it does **not** contain:

- Wi-Fi passwords intended to remain private.
- API keys.
- Private credentials.
- Personal access tokens.
- Private certificates.
- Production secrets.
- Sensitive deployment information.

Use `.gitignore` for local virtual environments, generated databases, logs, cache files, and secrets.

---

## 23. License

This repository is an academic project. Licensing terms can be added when the project team decides how the source code should be distributed.

---

## 24. Acknowledgement

Developed as a final-year project under the Department of Electronics and Communication Engineering, Sri Krishna College of Engineering & Technology, Coimbatore.
