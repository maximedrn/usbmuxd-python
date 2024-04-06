from socket import AddressFamily, socket, SOCK_STREAM
from typing import Any, Tuple, Union

from typing_extensions import Buffer

from usbmux.exceptions.exceptions import MuxError
from usbmux.exceptions.messages import Messages


Address = Union[Tuple[Any, ...], str, Buffer]


class SafeStreamSocket:
    """A class representing a safe stream socket.

    Attributes:
    -----------
        socket (socket): The underlying socket object.
    """

    def __init__(self, address: Address, family: AddressFamily):
        """Initializes a SafeStreamSocket object.

        Parameters:
        -----------
            address (Address): The address to connect to.
            family (AddressFamily): The address family 
                (e.g., AF_INET, AF_INET6).
        """
        self.__socket: socket = socket(family, SOCK_STREAM)
        self.__socket.connect(address)

    @property
    def socket(self) -> socket:
        """
        Returns the underlying socket object.

        Returns:
            The underlying socket object.
        """
        return self.__socket

    def send(self, message: bytes) -> None:
        """Sends the given message over the socket.

        Parameters:
        ----------
            message (bytes): The message to be sent.

        Raises:
        -------
            MuxError: If the socket connection is broken.
        """
        total_sent: int = 0
        while total_sent < len(message):
            if not (sent :=self.__socket.send(message[total_sent:])):
                raise MuxError(Messages.SOCKET_CONNECTION_BROKEN)
            total_sent += sent

    def receive(self, size: int) -> bytes:
        """Receives a specified number of bytes from the socket.

        Parameters:
        ----------
            size (int): The number of bytes to receive.

        Returns:
        --------
            bytes: The received bytes.

        Raises:
        -------
            MuxError: If the socket connection is broken.
        """
        message: bytes = bytes()
        while len(message) < size:
            if not (chunk := self.__socket.recv(size - len(message))):
                raise MuxError(Messages.SOCKET_CONNECTION_BROKEN)
            message += chunk
        return message
