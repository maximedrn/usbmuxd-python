from dataclasses import dataclass
from typing import Union

from usbmux.types.payload import Payload


@dataclass(frozen=True, init=False)
class Types:
    """Represents the types used in the USB multiplexing daemon."""
    RequestType = Union[str, int]
    Payload = Union[Payload, bytes]
