""" User defined protocol module """

ACK = 0x79
NACK = 0x1F
FIRMWARE_UPGRADE_MSGID = 0x012


def _get_command_payload(appbin):
    size = list((len(appbin) & 0XFFFF).to_bytes(2, "big"))
    return [*size, 0, 0, 0, 0, 0, 0]

def get_ack_packet():
    return [ACK, 0, 0, 0, 0, 0, 0, 0]

def get_nack_packet():
    return [NACK, 0, 0, 0, 0, 0, 0, 0]

def get_command_packet(appbin):
    msgid = FIRMWARE_UPGRADE_MSGID
    payload = _get_command_payload(appbin)
    return msgid, payload

def get_data_packet(appbin, packet_count):
    msgid = FIRMWARE_UPGRADE_MSGID
    start, end = packet_count * 8, (packet_count * 8) + 8
    payload = appbin[start: end]
    return msgid, payload
