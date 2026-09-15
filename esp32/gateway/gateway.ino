/*
 * OFFLINE COMMUNICATION SYSTEM
 *
 * ESP32 GATEWAY FIRMWARE
 *
 * Current stage:
 *
 *     Linux Laptop
 *          |
 *         USB
 *          |
 *        ESP32
 *
 * USB Serial Protocol:
 *
 *     PING
 *     STATUS
 *     ID
 *     HELP
 *
 * Future stages:
 *
 *     Wi-Fi
 *     LoRa
 *     Multi-hop routing
 *     Dashboard communication
 *     SOS
 *     GPS
 *     Voice
 */


// ============================================================
// CONFIGURATION
// ============================================================

#define NODE_ID "ESP32-GW-01"

const unsigned long SERIAL_BAUD = 115200;


// ============================================================
// GLOBALS
// ============================================================

String inputBuffer = "";


// ============================================================
// SETUP
// ============================================================

void setup() {

  Serial.begin(SERIAL_BAUD);

  delay(1000);


  Serial.println();

  Serial.println(
    "========================================"
  );

  Serial.println(
    " OFFLINE COMMUNICATION SYSTEM"
  );

  Serial.println(
    " ESP32 GATEWAY"
  );

  Serial.println(
    "========================================"
  );

  Serial.println(
    "NODE_ID=" NODE_ID
  );

  Serial.println(
    "STATUS=READY"
  );

  Serial.println(
    "BAUD=115200"
  );

  Serial.println(
    "----------------------------------------"
  );

  Serial.println(
    "Waiting for commands..."
  );

  Serial.println();
}


// ============================================================
// MAIN LOOP
// ============================================================

void loop() {

  readSerialCommands();

}


// ============================================================
// SERIAL COMMAND READER
// ============================================================

void readSerialCommands() {

  while (Serial.available() > 0) {

    char receivedChar = Serial.read();


    // --------------------------------------------------------
    // Ignore carriage return
    // --------------------------------------------------------

    if (receivedChar == '\r') {

      continue;

    }


    // --------------------------------------------------------
    // Newline = command complete
    // --------------------------------------------------------

    if (receivedChar == '\n') {

      inputBuffer.trim();


      if (inputBuffer.length() > 0) {

        processCommand(inputBuffer);

      }


      inputBuffer = "";

    }


    // --------------------------------------------------------
    // Normal character
    // --------------------------------------------------------

    else {

      if (inputBuffer.length() < 256) {

        inputBuffer += receivedChar;

      }


      else {

        Serial.println(
          "ERROR|COMMAND_TOO_LONG"
        );

        inputBuffer = "";

      }

    }

  }

}


// ============================================================
// COMMAND PROCESSOR
// ============================================================

void processCommand(String command) {

  command.trim();


  // ----------------------------------------------------------
  // Make command matching case-insensitive
  // ----------------------------------------------------------

  String upperCommand = command;

  upperCommand.toUpperCase();


  // ==========================================================
  // PING
  // ==========================================================

  if (upperCommand == "PING") {

    Serial.println(
      "PONG"
    );

  }


  // ==========================================================
  // STATUS
  // ==========================================================

  else if (upperCommand == "STATUS") {

    Serial.println(
      "STATUS|READY"
    );

    Serial.print(
      "NODE_ID|"
    );

    Serial.println(
      NODE_ID
    );

    Serial.print(
      "UPTIME_MS|"
    );

    Serial.println(
      millis()
    );

  }


  // ==========================================================
  // NODE ID
  // ==========================================================

  else if (upperCommand == "ID") {

    Serial.print(
      "NODE_ID|"
    );

    Serial.println(
      NODE_ID
    );

  }


  // ==========================================================
  // HELP
  // ==========================================================

  else if (upperCommand == "HELP") {

    Serial.println(
      "COMMANDS|PING,STATUS,ID,HELP"
    );

  }


  // ==========================================================
  // UNKNOWN COMMAND
  // ==========================================================

  else {

    Serial.print(
      "ERROR|UNKNOWN_COMMAND|"
    );

    Serial.println(
      command
    );

  }

}
