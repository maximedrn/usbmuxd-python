from typing import Final


class Messages:
    SOCKET_CONNECTION_BROKEN: Final[str] = "Socket connection broken."
    SOCKET_LISTENER_ERROR: Final[str] = "Exception in listener socket."
    SOCKET_IS_CONNECTED: Final[str] = (
        "Socket is connected, cannot process listener events.")
    TAG_MISMATCH: Final[str] = (
        "Tag mismatch: expected '{expected}', got '{current}'.")
    LISTEN_FAILED: Final[str] = "Listen failed. Error: {number}."
    CONNECTION_FAILED: Final[str] = "Connection failed. Error: {number}."
    UNEXPECTED_RESULT: Final[str] = "Unexpected result: {response}."
    INVALID_PAYLOAD: Final[str] = "Invalid payload type."
    INVALID_PACKET_TYPE: Final[str] = (
        "Invalid packet type received: {response}.")
    INVALID_OUTGOING_REQUEST_TYPE: Final[str] = (
        "Invalid outgoing request type '{request}'.")
    INVALID_INCOMING_RESPONSE_TYPE: Final[str] = (
        "Invalid incoming response type '{response}'.")
    MUX_CONNECTED_ERROR: Final[str] = (
        "Mux is connected, cannot issue control packets.")
    INVALID_VERSION: Final[str] = (
        "Version mismatch: expected '{expected}', got '{current}'.")
    INVALID_PLIST_TYPE: Final[str] = "Received non-plist type '{response}'."
