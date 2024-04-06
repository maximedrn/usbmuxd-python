from select import select
from socket import socket
from typing import List, Optional, Tuple, Type, Union

from usbmux.connection.device import Device
from usbmux.connection.protocols.protocol import Protocol
from usbmux.connection.safe_stream_socket import Address, SafeStreamSocket
from usbmux.connection.socket import Socket
from usbmux.exceptions.exceptions import MuxError
from usbmux.exceptions.messages import Messages
from usbmux.types.payload import _Properties as Properties, Payload
from usbmux.types.types import Types


class Connection:
    """Represents a connection to the USB multiplexing daemon.
    
    Attributes:
    ----------
        __socket (SafeStreamSocket): The safe stream socket.
        __protocol (Protocol): The protocol type.
        __devices (List[Device]): The list of connected devices.
        __packet_tag (int): The packet tag.
    """    

    def __init__(
        self, protocol: Type[Protocol], socket: Optional[Address] = None
    ) -> None:
        """Initializes a Connection object.

        Parameters:
        ----------
            protocol (Type[Protocol]): The protocol type.
            socket (Optional[Address]): The socket address. Defaults to None.
        """
        self.__socket: SafeStreamSocket = SafeStreamSocket(*Socket()(socket))
        self.__protocol: Protocol = protocol(self.__socket)
        self.__devices: List[Device] = []
        self.__packet_tag: int = 1

    @property
    def protocol(self) -> Protocol:
        """Returns the protocol type.

        Returns:
        --------
            Protocol: The protocol type.
        """
        return self.__protocol

    @property
    def devices(self) -> List[Device]:
        """Returns a list of connected devices.

        Returns:
        --------
            List[Device]: A list of Device objects representing 
            the connected devices.
        """
        return self.__devices

    @property
    def packet_tag(self) -> int:
        """Returns the packet tag.

        Returns:
        --------
            int: The packet tag.
        """
        return self.__packet_tag

    @packet_tag.setter
    def packet_tag(self, value: int) -> None:
        """Setter method for the packet tag.

        Parameters:
        ----------
            value (int): The new value for the packet tag.
        """
        self.__packet_tag = value

    def _get_reply(self) -> Tuple[int, Types.Payload]:
        """Get the reply from the protocol.

        Returns:
        --------
            A tuple containing the tag and data of the reply.

        Raises:
        -------
            MuxError: If the response packet type is invalid.
        """
        while True:
            response, tag, data = self.__protocol.get_packet()
            if response == self.__protocol.TYPE_RESULT:
                return tag, data
            error: str = Messages.INVALID_PACKET_TYPE
            raise MuxError(error.format(response=response))

    def _process_packet(self) -> None:
        """Process a packet received from the protocol.

        This method handles different types of responses received 
        from the protocol.
        - If the response is of type `TYPE_DEVICE_ADD`, it adds a new 
        device to the list of devices.
        - If the response is of type `TYPE_DEVICE_REMOVE`, it removes 
        the corresponding device from the list of devices.
        - If the response is not of type `TYPE_RESULT`, it raises a 
        `MuxError` with an appropriate error message.
        - If the response is of type `TYPE_RESULT`, it raises a 
        `MuxError` with an unexpected result error message.

        Raises:
        -------
            MuxError: If the response type is invalid or unexpected.
            MuxError: If the payload is invalid for `TYPE_DEVICE_ADD`
                or `TYPE_DEVICE_REMOVE`.
        """
        response, _, data = self.__protocol.get_packet()
        if response == self.__protocol.TYPE_DEVICE_ADD:
            if not isinstance(data, Payload):
                raise MuxError(Messages.INVALID_PAYLOAD)
            device_id: Union[int, None] = data.DeviceID
            properties: Union[Properties, None] = data.Properties
            if not isinstance(properties, Properties):
                return self.__devices.append(Device(device_id))
            product_id: Union[int, None] = properties.ProductID
            serial_number: Union[str, None] = properties.SerialNumber
            location_id: Union[int, None] = properties.LocationID
            return self.__devices.append(Device(  # Detected device.
                device_id, product_id, serial_number, location_id))
        if response == self.__protocol.TYPE_DEVICE_REMOVE:
            if not isinstance(data, Payload):
                raise MuxError(Messages.INVALID_PAYLOAD)
            [self.__devices.remove(device) for device in self.__devices 
             if device.device_id == data.DeviceID]
        if response != self.__protocol.TYPE_RESULT:
            error: str = Messages.INVALID_PACKET_TYPE
            raise MuxError(error.format(response=response))
        raise MuxError(Messages.UNEXPECTED_RESULT.format(response=response))

    def _exchange(
        self, request: Types.RequestType, payload: Payload = Payload()
    ) -> Union[int, None]:
        """Sends a request packet with the given payload and waits 
        for the reply.
        
        Parameters:
        ----------
            request (Types.RequestType): The type of request to send.
            payload (Payload, optional): The payload to include in the 
                request. Defaults to an empty payload.
        
        Returns:
        --------
            Union[int, None]: The number received in the reply packet, 
            or None if no reply was received.
        
        Raises:
        -------
            MuxError: If the received data is not a valid payload.
            MuxError: If the received tag does not match the expected tag.
        """
        previous_tag: int = self.__packet_tag
        self.__packet_tag += 1
        self.__protocol.send_packet(request, previous_tag, payload)
        received_tag, data = self._get_reply()
        if not isinstance(data, Payload):
            raise MuxError(Messages.INVALID_PAYLOAD)
        if received_tag != previous_tag:
            raise MuxError(Messages.TAG_MISMATCH.format(
                expected=previous_tag, current=received_tag))
        return data.Number

    def listen(self) -> None:
        """Listens for incoming connections.

        Raises:
        -------
            MuxError: If the listen operation fails.
        """
        if (number := self._exchange(self.__protocol.TYPE_LISTEN)):
            raise MuxError(Messages.LISTEN_FAILED.format(number=number))

    def process(self, timeout: Optional[float] = None) -> None:
        """Process the listener events and handle incoming packets.

        Parameters:
        ----------
            timeout (Optional[float]): The maximum time to wait for 
                events, in seconds. Defaults to None.

        Raises:
        -------
            MuxError: If the socket is already connected or if there 
            is an error with the socket listener.
        """
        if self.__protocol.connected:
            raise MuxError(Messages.SOCKET_IS_CONNECTED)
        socket_list: List[socket] = [self.__socket.socket]
        rlo, _, xlo = select(socket_list, [], socket_list, timeout)
        if xlo:  # Cannot process listener events.
            self.close()
            raise MuxError(Messages.SOCKET_LISTENER_ERROR)
        if rlo:  # Process listener events.
            self._process_packet()

    def connect(self, device: Device, port: int) -> socket:
        """Connects to the specified device and port.

        Parameters:
        ----------
            device (Device): The device to connect to.
            port (int): The port number to connect to.

        Returns:
        --------
            socket: The connected socket.

        Raises:
        -------
            MuxError: If the connection fails.
        """
        device_id: Union[int, None] = device.device_id
        port_number: int = ((port << 8) & 0xFF00) | (port >> 8)
        payload: Payload = Payload(DeviceID=device_id, PortNumber=port_number)
        request: Types.RequestType = self.__protocol.TYPE_CONNECT
        if not (number := self._exchange(request, payload)):
            raise MuxError(Messages.CONNECTION_FAILED.format(number=number))
        self.__protocol.connected = True
        return self.__socket.socket

    def close(self) -> None:
        """Closes the connection by closing the underlying socket."""
        self.__socket.socket.close()
