# -*- coding: utf-8 -*-

from socket import socket
from typing import List, Optional, Type, Union

from usbmux.connection.connection import Connection
from usbmux.connection.device import Device
from usbmux.connection.protocols.binary_protocol import BinaryProtocol
from usbmux.connection.protocols.plist_protocol import PlistProtocol
from usbmux.connection.protocols.protocol import Protocol
from usbmux.exceptions.exceptions import MuxVersionError


class USBMux:

    def __init__(self, socket_path: Optional[str] = None) -> None:
        self.__socket_path: Union[str, None] = socket_path
        try:  # Try to connect using the binary protocol first.
            self.__connect(BinaryProtocol, 0)
        except MuxVersionError:  # Otherwise, use the plist protocol.
            self.__connect(PlistProtocol, 1)
        self.devices: List[Device] = self.__listener.devices

    def __connect(self, protocol: Type[Protocol], version: int) -> None:
        self.__listener: Connection = Connection(protocol, self.__socket_path)
        self.__listener.listen()
        self.__version: int = version
        self.__protocol = protocol

    def process(self, timeout: float = 10):
        self.__listener.process(timeout)

    def connect(self, device: Device, port: int) -> socket:
        connector = Connection(self.__protocol, self.__socket_path)
        return connector.connect(device, port)



