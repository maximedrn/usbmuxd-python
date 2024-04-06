from dataclasses import dataclass
from typing import Tuple, Union


@dataclass(frozen=True, init=False)
class Payloads:
    """Represents the payloads used in the USB multiplexing daemon."""
    IH256sHI = Tuple[int, int, str, int, int]
    I = Tuple[int]
    III = Tuple[int, int, int]
    IIII = Tuple[int, int, int, int]
    IH = Tuple[Union[int, None], Union[int, None]]
