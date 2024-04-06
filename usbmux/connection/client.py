from plistlib import loads
from typing import Any, Dict, Final

from usbmux.connection.connection import Connection
from usbmux.connection.protocols.plist_protocol import PlistProtocol
from usbmux.exceptions.exceptions import MuxError
from usbmux.exceptions.messages import Messages
from usbmux.types.payload import Payload


class Client(Connection):
    
    TYPE_READ_PAIR: Final[str] = "ReadPairRecord"

    def __init__(self):
        super(Client, self).__init__(PlistProtocol)

    def get_pair_record(self, udid: str) -> Dict[str, Any]:
        tag: int = self.packet_tag
        self.packet_tag += 1
        payload: Payload = Payload(PairRecordID=udid)
        self.protocol.send_packet(self.TYPE_READ_PAIR, tag, payload)
        _, received_tag, data = self.protocol.get_packet()
        if received_tag != tag:
            raise MuxError(Messages.TAG_MISMATCH.format(
                excepted=tag, current=received_tag))
        if not isinstance(data, Payload):
            raise MuxError(Messages.INVALID_PAYLOAD)
        if not isinstance(data.PairRecordData, bytes):
            raise MuxError(Messages.INVALID_PAYLOAD)
        return loads(data.PairRecordData)
