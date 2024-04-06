from socket import AddressFamily
from sys import platform
from typing import Final, List, Optional, Tuple

from usbmux.connection.safe_stream_socket import Address


class Socket:
    """A class representing a socket.

    Attributes:
    ----------
        WINDOWS (List[str]): A list of strings representing Windows platforms.
    """

    WINDOWS: Final[List[str]] = ["win32", "cygwin"]

    def __init__(self) -> None:
        """Initializes a new instance of the Socket class."""
        self.__is_nt: bool = platform in self.WINDOWS

    def __address(self, socket: Optional[Address] = None) -> Address:
        """Returns the address for the given socket.

        Parameters:
        ----------
            socket (Optional[Address]): The socket to get the address for.
                Defaults to None.

        Returns:
        --------
            Address: The address of the socket.
        """
        if self.__is_nt:
            return "127.0.0.1", 27015
        return socket if socket else "/var/run/usbmuxd"

    def __socket(self) -> AddressFamily:
        """Returns the address family for creating a socket.

        If the operating system is Windows, it returns AF_INET.
        Otherwise, it returns AF_UNIX.

        Returns:
        --------
            The address family for creating a socket.
        """
        if self.__is_nt:
            from socket import AF_INET  # type: ignore
            return AF_INET
        from socket import AF_UNIX  # type: ignore
        return AF_UNIX

    def __call__(
        self, socket: Optional[Address] = None
    ) -> Tuple[Address, AddressFamily]:
        """Calls the object as a function.

        Parameters:
        ----------
            socket (Optional[Address]): The socket address. Defaults to None.

        Returns:
        --------
            Tuple[Address, AddressFamily]: A tuple containing the 
            address and address family.
        """
        return self.__address(socket), self.__socket()
