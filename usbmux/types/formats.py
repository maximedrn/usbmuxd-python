from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, init=False)
class Formats:
    """Represents the formats used in the USB multiplexing daemon."""
    I: Final[str] = "I"
    III: Final[str] = "III"
    IIII: Final[str] = "IIII"
    IH256sHI: Final[str] = "IH256sHI"
    IH: Final[str] = "IH"
