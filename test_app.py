import sys
import can

import protocol

# CAN bus configurations
CHANNEL = "vcan0"
INTERFACE = "socketcan"

# Available bytes
MAX_APPBIN_SIZE = 64000

def create_canbus(channel, interface):
    canbus = can.Bus(channel=channel, interface=interface)
    return canbus

def _send_ack_byte(canbus):
    msgid = protocol.FIRMWARE_UPGRADE_MSGID
    payload = protocol.get_ack_packet()
    command = can.Message(arbitration_id=msgid, data=payload)
    canbus.send(command)

def _recv_firmware_bytes(canbus, packet_size):
    appbin_bytes = []

    for i in range(packet_size + 1):
        packet = canbus.recv(timeout=2)
        appbin_bytes.extend(list(packet.data[0:8]))

    return appbin_bytes

def _validate_checksum(appbin):
    checksum = appbin[-1]
    sumbytes = sum(appbin[:-1]) & 0xFF
    print("checksum: {}, sumbytes: {}".format(checksum, sumbytes))
    return checksum == sumbytes

def recv_appbin(canbus):
    appbin = []
    msg = canbus.recv(timeout=2)

    if msg.arbitration_id == protocol.FIRMWARE_UPGRADE_MSGID:
        appbin_size = (msg.data[0] << 8) | msg.data[1]

        if appbin_size >= MAX_APPBIN_SIZE:
            return None, "Invaild size"

        _send_ack_byte(canbus)
        packet_size = appbin_size // 8
        appbin = _recv_firmware_bytes(canbus, packet_size)

        if not _validate_checksum(appbin):
            return None, "Invalid checksum"

        _send_ack_byte(canbus)
    return appbin, ""

def main():
    canbus = create_canbus(CHANNEL, INTERFACE)
    appbin = recv_appbin(canbus)

    if appbin[0] == None:
        print("Err: {}".format(appbin[1]))
        sys.exit(1)

    print("Recieved total bytes: {}".format(len(appbin[0][:-1])))


if __name__ == "__main__":
    main()
