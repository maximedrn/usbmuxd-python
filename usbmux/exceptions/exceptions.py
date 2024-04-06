class MuxError(Exception):
    """Custom exception class for USB Mux errors."""
    pass


class MuxVersionError(MuxError):
    """Exception raised when there is a version mismatch in the 
    USBMux protocol.
    """
    pass
