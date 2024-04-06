from dataclasses import asdict
from plistlib import dumps, loads
from typing import Any, Dict, Final, Tuple

from usbmux.connection.protocols.binary_protocol import BinaryProtocol
from usbmux.connection.safe_stream_socket import SafeStreamSocket
from usbmux.exceptions.exceptions import MuxError
from usbmux.exceptions.messages import Messages
from usbmux.types.payload import _Properties, Payload
from usbmux.types.types import Types


class PlistProtocol(BinaryProtocol):

    TYPE_RESULT: Final[str] = "Result"
    TYPE_CONNECT: Final[str] = "Connect"
    TYPE_LISTEN: Final[str] = "Listen"
    TYPE_DEVICE_ADD: Final[str] = "Attached"
    TYPE_DEVICE_REMOVE: Final[str] = "Detached"
    TYPE_PLIST: Final[int] = 8
    VERSION: Final[int] = 1

    def __init__(self, socket: SafeStreamSocket) -> None:
        """Initialize a new instance of the PlistProtocol class.

        Parameters:
        -----------
            socket (SafeStreamSocket): The socket object used 
                for communication.
        """
        BinaryProtocol.__init__(self, socket)

    def _unpack(self, response: int, payload: bytes) -> bytes:
        """Unpacks the payload received from the response.

        Parameters:
        -----------
            response (int): The response code.
            payload (bytes): The payload data.

        Returns:
        --------
            bytes: The unpacked payload.
        """
        return payload

    def __request_type(self, request: Types.RequestType) -> str:
        """Determines the type of request based on the given input.

        Parameters:
        -----------
            request (Types.RequestType): The request to determine 
                the type for.

        Returns:
        --------
            str: The type of the request.
        """
        if not isinstance(request, int):
            return request
        return {2: self.TYPE_CONNECT, 3: self.TYPE_LISTEN}[request]

    def send_packet(
        self, request: Types.RequestType, tag: int, payload: Payload
    ) -> None:
        """Sends a packet with the specified request and tag.

        Parameters:
        -----------
            request (Types.RequestType): The request to send. It can be 
                either a string or an integer.
            tag (int): The tag associated with the packet.
        """
        def remove_none(dict: Dict[str, Any]) -> Dict[str, Any]:
            """Removes key-value pairs with None values from a dictionary.

            Parameters:
            -----------
                dict (Dict[str, Any]): The input dictionary.

            Returns:
            --------
                Dict[str, Any]: A new dictionary with the None values removed.
            """
            return {key: value for key, value in dict.items()
                    if value is not None}
        
        payload.MessageType = self.__request_type(request)
        wrapped_payload: bytes = dumps(remove_none(asdict(payload)))
        BinaryProtocol.send_packet(self, self.TYPE_PLIST, tag, wrapped_payload)

    def get_packet(self) -> Tuple[str, int, Payload]:
        """Retrieves a packet from the binary protocol.

        Returns:
        --------
            A tuple containing the response, tag, and structured payload.

        Raises:
        -------
            MuxError: If the received response is not of type 'plist'.
        """
        response, tag, payload = BinaryProtocol.get_packet(self)
        if response != self.TYPE_PLIST:
            error: str = Messages.INVALID_INCOMING_RESPONSE_TYPE
            raise MuxError(error.format(response=response))
        if isinstance(payload, Payload):
            return payload.MessageType or '', tag, payload
        # Output of BinaryProtocol.get_packet() is a bytes object because
        # it uses the PlistProtocol._unpack() method which does not
        # transform the payload into a structured object (overridden).
        plist_payload: Dict[str, Any] = loads(payload)
        properties: Dict[str, Any] = plist_payload.pop('Properties', {})
        structured_payload: Payload = Payload(
            **plist_payload, Properties=_Properties(**properties))
        string_response: str = structured_payload.MessageType or ''
        return string_response, tag, structured_payload
