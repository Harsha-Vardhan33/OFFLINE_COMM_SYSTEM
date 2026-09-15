"""
OFFLINE COMMUNICATION SYSTEM

ESP32 Gateway Service

Communication path:

Flask
  |
  v
ESP32Gateway
  |
  v
PySerial
  |
  v
/dev/ttyUSB0
  |
  v
USB
  |
  v
ESP32
"""


import threading
import time

import serial
from serial import SerialException


# ============================================================
# CONFIGURATION
# ============================================================

ESP32_SERIAL_PORT = "/dev/ttyUSB0"

ESP32_BAUD_RATE = 115200

SERIAL_TIMEOUT = 0.5

COMMAND_TIMEOUT = 3.0


# ============================================================
# ESP32 GATEWAY
# ============================================================

class ESP32Gateway:

    def __init__(
        self,
        port=ESP32_SERIAL_PORT,
        baud_rate=ESP32_BAUD_RATE
    ):

        self.port = port
        self.baud_rate = baud_rate

        self.serial_connection = None

        self.lock = threading.Lock()

        self.connected = False

        self.last_error = None

        self.last_command = None

        self.last_response = []


    # ========================================================
    # CONNECT
    # ========================================================

    def connect(self):

        if self.serial_connection is not None:

            if self.serial_connection.is_open:

                self.connected = True

                return True


        try:

            print(
                "[ESP32] Opening serial port: "
                + self.port
            )

            print(
                "[ESP32] Baud rate: "
                + str(self.baud_rate)
            )


            self.serial_connection = serial.Serial(

                port=self.port,

                baudrate=self.baud_rate,

                timeout=SERIAL_TIMEOUT

            )


            # Opening the serial port may reset the ESP32.
            time.sleep(2)


            # Remove ESP32 startup messages from the buffer.
            self.serial_connection.reset_input_buffer()


            self.connected = True

            self.last_error = None


            print(
                "[ESP32] Serial connection established."
            )


            return True


        except SerialException as error:

            self.connected = False

            self.last_error = str(error)


            print(
                "[ESP32] Connection failed: "
                + str(error)
            )


            return False


    # ========================================================
    # DISCONNECT
    # ========================================================

    def disconnect(self):

        with self.lock:

            if self.serial_connection is not None:

                try:

                    self.serial_connection.close()

                except Exception:

                    pass


            self.serial_connection = None

            self.connected = False


            print(
                "[ESP32] Serial connection closed."
            )


    # ========================================================
    # SEND COMMAND
    # ========================================================

    def send_command(self, command):

        with self.lock:

            self.last_command = command

            self.last_response = []


            # ------------------------------------------------
            # CONNECT
            # ------------------------------------------------

            if not self.connect():

                return {

                    "success": False,

                    "error": self.last_error

                }


            try:

                # --------------------------------------------
                # CLEAR OLD INPUT
                # --------------------------------------------

                self.serial_connection.reset_input_buffer()


                # --------------------------------------------
                # SEND COMMAND
                # --------------------------------------------

                message = command.strip() + "\n"


                self.serial_connection.write(
                    message.encode("utf-8")
                )


                self.serial_connection.flush()


                print(
                    "[ESP32] Laptop -> ESP32: "
                    + command
                )


                # --------------------------------------------
                # READ RESPONSE
                # --------------------------------------------

                responses = []

                deadline = (
                    time.monotonic()
                    + COMMAND_TIMEOUT
                )


                while time.monotonic() < deadline:

                    line = (
                        self.serial_connection.readline()
                    )


                    if not line:

                        continue


                    response = line.decode(
                        "utf-8",
                        errors="replace"
                    ).strip()


                    if response:

                        responses.append(response)


                        print(
                            "[ESP32] ESP32 -> Laptop: "
                            + response
                        )


                        # ------------------------------------
                        # PING
                        # ------------------------------------

                        if command.upper() == "PING":

                            if response == "PONG":

                                break


                        # ------------------------------------
                        # ID
                        # ------------------------------------

                        elif command.upper() == "ID":

                            if response.startswith(
                                "NODE_ID|"
                            ):

                                break


                        # ------------------------------------
                        # STATUS
                        # ------------------------------------

                        elif command.upper() == "STATUS":

                            if len(responses) >= 3:

                                break


                        # ------------------------------------
                        # HELP
                        # ------------------------------------

                        elif command.upper() == "HELP":

                            if response.startswith(
                                "COMMANDS|"
                            ):

                                break


                        # ------------------------------------
                        # OTHER COMMANDS
                        # ------------------------------------

                        else:

                            break


                self.last_response = responses


                # --------------------------------------------
                # NO RESPONSE
                # --------------------------------------------

                if not responses:

                    return {

                        "success": False,

                        "error":
                            "No response from ESP32",

                        "command": command,

                        "response": []

                    }


                # --------------------------------------------
                # SUCCESS
                # --------------------------------------------

                return {

                    "success": True,

                    "command": command,

                    "response": responses

                }


            except SerialException as error:

                self.connected = False

                self.last_error = str(error)


                print(
                    "[ESP32] Serial communication error: "
                    + str(error)
                )


                return {

                    "success": False,

                    "error": str(error)

                }


    # ========================================================
    # PING
    # ========================================================

    def ping(self):

        result = self.send_command("PING")


        if not result.get("success"):

            return result


        if "PONG" not in result.get(
            "response",
            []
        ):

            return {

                "success": False,

                "error":
                    "Unexpected response from ESP32",

                "response":
                    result.get("response", [])

            }


        return result


    # ========================================================
    # STATUS
    # ========================================================

    def status(self):

        return self.send_command("STATUS")


    # ========================================================
    # NODE ID
    # ========================================================

    def get_id(self):

        return self.send_command("ID")


# ============================================================
# SINGLE GATEWAY INSTANCE
# ============================================================

esp32_gateway = ESP32Gateway()
