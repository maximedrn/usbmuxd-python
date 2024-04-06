from struct import pack, unpack
from typing import Tuple

from usbmux.connection.protocols.protocol import Protocol
from usbmux.connection.safe_stream_socket import SafeStreamSocket
from usbmux.exceptions.exceptions import MuxError, MuxVersionError
from usbmux.exceptions.messages import Messages
from usbmux.types.payload import _Properties as Properties, Payload
from usbmux.types.formats import Formats
from usbmux.types.payloads import Payloads
from usbmux.types.types import Types


class BinaryProtocol(Protocol):

    TYPE_RESULT: int = 1
    TYPE_CONNECT: int = 2
    TYPE_LISTEN: int = 3
    TYPE_DEVICE_ADD: int = 4
    TYPE_DEVICE_REMOVE: int = 5
    VERSION: int = 0
    PADDING_LENGTH: int = 16
    SOCKET_PADDING: int = 4

    def __init__(self, socket: SafeStreamSocket) -> None:
        """Initializes a new instance of the BinaryProtocol class.

        Parameters:
        -----------
            socket (SafeStreamSocket): The socket object used 
                for communication.
        """
        self.__socket: SafeStreamSocket = socket
        self.__connected: bool = False

    @property
    def connected(self) -> bool:
        """Returns the connection status of the object.

        Returns:
        --------
            bool: True if the object is connected, False otherwise.
        """
        return self.__connected

    @connected.setter
    def connected(self, value: bool) -> None:
        """Setter method for the 'connected' attribute.

        Parameters:
        -----------
            value (bool): The new value for the 'connected' attribute.
        """
        self.__connected = value

    def __is_connected(self) -> None:
        """Checks if the device is connected.

        Raises:
        -------
            MuxError: If the device is already connected.
        """
        if self.connected:
            raise MuxError(Messages.MUX_CONNECTED_ERROR)

    def _pack(self, request: int, payload: Types.Payload) -> bytes:
        """Packs the request and payload into a binary representation.

        Parameters:
        -----------
            request (int): The type of request.
            payload (Types.Payload): The payload object containing the 
                data to be packed.

        Returns:
        --------
            bytes: The binary representation of the packed request 
            and payload.

        Raises:
        -------
            ValueError: If the request type is invalid.
        """
        if not isinstance(payload, Payload):
            return payload  # No need to pack the payload.
        if request == self.TYPE_LISTEN:
            return bytes()  # No payload for listen request.
        if request == self.TYPE_CONNECT:
            connection_data: bytes = b"\x00\x00"
            data: Payloads.IH = payload.DeviceID, payload.PortNumber
            wrapped_payload: bytes = pack(Formats.IH, *data)
            return wrapped_payload + connection_data
        error: str = Messages.INVALID_OUTGOING_REQUEST_TYPE
        raise ValueError(error.format(request=request))

    def _unpack(self, response: int, payload: Types.Payload) -> Payload:
        """Unpacks the response payload based on the response type.

        Parameters:
        -----------
            response (int): The response type.
            payload (Types.Payload): The payload data.

        Returns:
        --------
            Payload: The unpacked payload object.

        Raises:
        -------
            MuxError: If the response type is invalid.
        """
        if isinstance(payload, Payload):
            raise NotImplementedError()
        if response == self.TYPE_RESULT:  # Result payload.
            result_payload: Payloads.I = unpack(Formats.I, payload)
            return Payload(Number=result_payload[0])
        if response == self.TYPE_DEVICE_REMOVE: # Device remove payload.
            remove_payload: Payloads.I = unpack(Formats.I, payload)
            return Payload(DeviceID=remove_payload[0])
        if response == self.TYPE_DEVICE_ADD:  # Device add payload.
            add_payload: Payloads.IH256sHI = unpack(Formats.IH256sHI, payload)
            device_id, product_id, serial_number, _, location = add_payload
            serial_number: str = serial_number.split("\0")[0]
            properties: Properties = Properties(
                LocationID=location, SerialNumber=serial_number, 
                ProductID=product_id)  # Device properties.
            return Payload(DeviceID=device_id, Properties=properties)
        error: str = Messages.INVALID_INCOMING_RESPONSE_TYPE
        raise MuxError(error.format(response=response))

    def send_packet(
        self, request: int, tag: int, payload: Types.Payload
    ) -> None:
        """Sends a packet to the connected device.

        Parameters:
        -----------
            request (int): The request identifier.
            tag (int): The tag identifier.
            payload (Types.Payload): The payload to be sent.
        """
        self.__is_connected()  # Check if the device is connected.
        wrapped_payload: bytes = self._pack(request, payload)
        length: int = self.PADDING_LENGTH + len(wrapped_payload)
        data: Payloads.IIII = length, self.VERSION, request, tag
        self.__socket.send(pack(Formats.IIII, *data) + wrapped_payload)

    def get_packet(self) -> Tuple[int, int, Types.Payload]:
        """Retrieves a packet from the device.

        Returns:
        --------
            Tuple[int, int, Types.Payload]: A tuple containing the 
            response code, tag, and payload of the packet.

        Raises:
        -------
            MuxVersionError: If the version of the packet is invalid.
        """
        self.__is_connected()  # Check if the device is connected.
        received_data: bytes = self.__socket.receive(self.SOCKET_PADDING)
        length_payload: Payloads.I = unpack(Formats.I, received_data)
        size: int = length_payload[0] - self.SOCKET_PADDING
        body: bytes = self.__socket.receive(size)
        payload: Payloads.III = unpack(Formats.III, body[:0xc])
        version, response, tag = payload
        if version == self.VERSION:
            return response, tag, self._unpack(response, body[0xc:])
        raise MuxVersionError(Messages.INVALID_VERSION.format(
            expected=self.VERSION, current=version))
