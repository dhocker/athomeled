#
# AtHomeLED -  CircuitPython_DotStarAPA102 driver adapter
# Copyright © 2019  Dave Hocker (AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

import board
import busio
from adafruit_bus_device import spi_device
from circuitpython_dotstarapa102.dotstarapa102 import DotStarAPA102
from .driver_base import DriverBase


class CPDotStarAPA102Driver(DriverBase):
    """
    A device driver must implement each of the methods in the DriverBase class.
    The driver class name is arbitrary and generally is not exposed.
    Add the driver to the app by modifying the driver.manager.get_driver()
    method.
    """

    def __init__(self):
        DriverBase.__init__(self)

    @property
    def name(self):
        return "CircuitPythonDotStarAPA102Driver"

    @property
    def Device(self):
        """
        Returns the wrapped usb.core.Device instance.
        Refer to the usb.core.Device class for details of the Device class.
        """
        return self._strip

    def open(self, num_pixels, datapin=10, clockpin=11, order='bgr'):
        """
        Open/initialize the LED string connected to the standard SPI interface.
        :param num_pixels: Number of LEDs in the string
        :param datapin: Not used, ignored. The standard SPI interface is used.
        :param clockpin: Not used, ignored. The standard SPI interface is used.
        :param order: The color order used by the string. Note that the default
        color order is reversed from the typcial 'rgb' order.
        :return:
        """
        self._numpixels = num_pixels
        self._order = order
        # Try to create an SPI device for the onboard SPI interface
        # We are using the standard SPI pins
        # SCLK = #23 (clock)
        # MOSI = #19 (data out)
        # MISO = #21 (data in, not used here)
        self._spi_bus = busio.SPI(board.SCLK, MOSI=board.MOSI, MISO=board.MISO)
        
        # Wrap the SPI bus in a context manager
        # The baudrate here is believed to be the maximum for an RPi
        # Reference: https://www.corelis.com/education/tutorials/spi-tutorial/
        # Reference: https://learn.adafruit.com/circuitpython-basics-i2c-and-spi/spi-devices
        # See references for a description of polarity and phase.
        # DotStars were found to work with either polarity=1 and phase=0 (mode 2)
        # or polarity=0 and phase=1 (mode 1). They did not work properly with
        # the default values polarity=0 and phase=0 (mode 0) or with 
        # polarity=1 and phase=1 (mode 3)..
        # Looking at the APA102C datasheet indicates that it samples the data
        # line on the trailing edge of the clock pulse. SPI mode 1 and 2 is set up
        # for the device to sample the data line on the falling edge of the
        # clock which seems to be more compatible with the APA102C.
        self._spi_dev = spi_device.SPIDevice(self._spi_bus, baudrate=15000000, polarity=1, phase=0)

        # Create driver from the context manager
        self._driver = DotStarAPA102(self._spi_dev, self._num_pixels, order=self._order)

        return self._begin()

    def _begin(self):
        return True

    def show(self):
        """
        Transmit all pixels to the LED string.
        :return:
        """
        self._driver.show()
        return True

    def numPixels(self):
        return self._numpixels

    def setBrightness(self, brightness):
        """
        Set the global brightness level
        :param brightness: 0-255
        :return:
        """
        # Driver brightness is 0-31, so we simply scale it here
        self._driver.global_brightness = int(brightness / 8)
        return True

    def setPixelColor(self, index, color_value):
        """
        Set the color of a given pixel
        :param index: pixel 0-n where n = num_pixels - 1
        :param color_value: A color value in the form 0xRRGGBB.
        :return:
        """
        self._driver.set_pixel_color(index, color_value)
        return True

    def clear(self):
        """
        Set all pixels to off.
        :return:
        """
        self._driver.clear()
        return True

    def close(self):
        """
        Close and release the current device.
        :return: None
        """
        self._driver.clear()
        # Not absolutely required but here for completeness
        self._spi_bus.deinit();
        return True

    def color(self, r, g, b, gamma=False):
        # Based on empiracle observation when the order is rgb
        # when order='rgb'
        if gamma:
            return (self.gamma8[b] << 16) | (self.gamma8[g] << 8) | self.gamma8[r]
        return (b << 16) | (g << 8) | r
