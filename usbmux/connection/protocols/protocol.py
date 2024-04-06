
from abc import ABC, abstractmethod
from typing import Tuple, Union

from usbmux.connection.safe_stream_socket import SafeStreamSocket
from usbmux.types.types import Types


class Protocol(ABC):
    """An abstract class representing a protocol."""

    TYPE_RESULT: Union[int, str]
    TYPE_CONNECT: Union[int, str]
    TYPE_LISTEN: Union[int, str]
    TYPE_DEVICE_ADD: Union[int, str]
    TYPE_DEVICE_REMOVE: Union[int, str]
    VERSION: int

    @abstractmethod
    def __init__(self, socket: SafeStreamSocket) -> None:
        """Initializes a new instance of the Protocol class.

        Parameters:
        -----------
            socket (SafeStreamSocket): The socket object used 
                for communication.
        """
        pass

    @property
    @abstractmethod
    def connected(self) -> bool:
        """Returns the connection status of the object.

        Returns:
        --------
            bool: True if the object is connected, False otherwise.
        """
        pass

    @connected.setter
    @abstractmethod
    def connected(self, value: bool) -> None:
        """Setter method for the 'connected' attribute.

        Parameters:
        -----------
            value (bool): The new value for the 'connected' attribute.
        """
        pass

    @abstractmethod
    def send_packet(
        self, request: Types.RequestType, tag: int, payload: Types.Payload
    ) -> None:
        """Sends a packet to the connected device.

        Parameters:
        -----------
            request (int): The request identifier.
            tag (int): The tag identifier.
            payload (Types.Payload): The payload to be sent.
        """
        pass

    @abstractmethod
    def get_packet(self) -> Tuple[Union[int, str], int, Types.Payload]:
        """Retrieves a packet from the socket.

        Returns:
        --------
            Tuple[Union[int, str], int, Types.Payload]: The packet 
                received from the socket.
        """
        pass
