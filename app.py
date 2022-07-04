import sys
import json

import can
import protocol


def read_appbin(filename):
    with open(filename, "rb") as appbin:
        appbin_bytes = appbin.read()

    appbin = list(appbin_bytes)
    checksum = sum(appbin) & 0xFF
    appbin.append(checksum)
    return appbin

def create_canbus(channel, interface):
    canbus = can.Bus(channel=channel, interface=interface)
    return canbus

def _send_command(canbus, msgid, payload):
    command = can.Message(arbitration_id=msgid, data=payload)
    canbus.send(command)
    response = canbus.recv(timeout=2)
    return response

def _send_data(canbus, msgid, payload):
    command = can.Message(arbitration_id=msgid, data=payload)
    canbus.send(command)

def send_appbin(canbus, appbin):
    msgid, payload = protocol.get_command_packet(appbin)
    response = _send_command(canbus, msgid, payload)
    packet_count = 0

    if response.data[0] == protocol.NACK:
        return response

    while True:
        msgid, payload = protocol.get_data_packet(appbin, packet_count)
        if len(payload) == 0:
            break

        _send_data(canbus, msgid, payload)
        packet_count += 1

    response = canbus.recv(timeout=2)
    return response

def main():
    if len(sys.argv) == 1:
        print("Syntax Error: python app.py <config file>")
        sys.exit(1)

    with open(sys.argv[1], "r") as configfile:
        config = json.loads(configfile.read())

    canbus = create_canbus(config["CHANNEL"], config["INTERFACE"])
    appbin = read_appbin(config["APPBIN"])
    response = send_appbin(canbus, appbin)

    if response.data[0] == protocol.NACK:
        print("Error: id = {}".format(response.data[1]))
        sys.exit(2)

    print("Info: Successfully sent application binary")


if __name__ == "__main__":
    main()
