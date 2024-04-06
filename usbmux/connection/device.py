from typing import Final, Optional, Union


class Device:
    """Represents a device connected to the USB multiplexing daemon.

    Attributes:
    -----------
        STRING (Final[str]): A string template for the string 
            representation of the Device object.
    """

    STRING: Final[str] = (
        "<%s: Device ID %d, USB Product ID 0x%04x, "
        "Serial '%s', Location 0x%x>"
    )

    def __init__(
            self, device_id: Optional[int] = None,
            usb_product_id: Optional[int] = None,
            serial: Optional[str] = None,
            location: Optional[int] = None
        ) -> None:
        """Initialize a Device object.

        Parameters:
        ----------
            device_id (Optional[int]): The device ID. 
                Defaults to None.
            usb_product_id (Optional[int]): The USB product ID. 
                Defaults to None.
            serial (Optional[str]): The device serial number.
                Defaults to None.
            location (Optional[int]): The device location. 
                Defaults to None.
        """
        self.__device_id: Union[int, None] = device_id
        self.__usb_product_id: Union[int, None] = usb_product_id
        self.__serial: Union[str, None] = serial
        self.__location: Union[int, None] = location

    @property
    def device_id(self) -> Union[int, None]:
        """Returns the ID of the device.

        Returns:
        --------
            Union[int, None]: The ID of the device.
        """
        return self.__device_id

    def __str__(self) -> str:
        """Returns a string representation of the Device object.
        
        The string representation includes the device ID, USB product ID,
        serial number, and location of the device.
        
        Returns:
        --------
            str: A string representation of the Device object.
        """
        instance: str = __name__ + '.' + __class__.__name__
        return self.STRING % (
            instance, self.__device_id, self.__usb_product_id, 
            self.__serial, self.__location)
