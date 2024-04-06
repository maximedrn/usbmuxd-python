from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=False, init=True, kw_only=True)
class _Properties:
    """Represents the properties of a payload."""
    ConnectionType: Optional[str] = None
    DeviceID: Optional[int] = None
    LocationID: Optional[int] = None
    ProductID: Optional[int] = None
    SerialNumber: Optional[str] = None
    UDID: Optional[str] = None


@dataclass(frozen=False, init=True, kw_only=True)
class Payload:
    """Represents a payload sent to the USB multiplexing daemon."""
    ClientVersionString: str = "qt4i-usbmuxd"
    ProgName: str = "tcprelay"
    MessageType: Optional[str] = None
    Number: Optional[int] = None
    DeviceID: Optional[int] = None
    PortNumber: Optional[int] = None
    Properties: Optional[_Properties] = None
    PairRecordID: Optional[str] = None
    PairRecordData: Optional[bytes] = None
