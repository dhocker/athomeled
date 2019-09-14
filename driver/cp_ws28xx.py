#
# AtHomeLED -  Adafruit_CircuitPython_WS2801 driver adapter
# Copyright © 2019  Dave Hocker (AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#
# This adapter allows AtHomeLED to use the Adafruit CP WS2801 driver
# even though the Adafruit API is significantly different from
# the legacy rpi-ws281x driver.
#

import board
import busio
from adafruit_bus_device import spi_device
import neopixel
from .driver_base import DriverBase
import logging

logger = logging.getLogger("led")


class AdafruitCircuiPythonWS28xxDriver(DriverBase):
    """
    A device driver must implement each of the methods in the DriverBase class.
    The driver class name is arbitrary and generally is not exposed.
    Add the driver to the app by modifying the driver.manager.get_driver()
    method.
    """
    # The NeoPixel driver is problematic. Once the driver is created
    # it can't be recreated. Thus, we manage it as a singleton.
    _driver = None

    # Convert color order to tuple
    _color_order = {
        "b": 0,
        "g": 1,
        "r": 2
    }

    def __init__(self):
        DriverBase.__init__(self)

    def __del__(self):
        """
        Class destructor. Note that there is a memory leak in the NeoPixel
        driver which will show as an error message when the using program
        exits.
        """
        # Delete the singleton NeoPixel driver instance once and only once
        if AdafruitCircuiPythonWS28xxDriver._driver:
            AdafruitCircuiPythonWS28xxDriver._driver.deinit()
            del AdafruitCircuiPythonWS28xxDriver._driver
            AdafruitCircuiPythonWS28xxDriver._driver = None

    @property
    def name(self):
        return "AdafruitCircuiPythonWS28xxDriver"

    @property
    def Device(self):
        """
        Returns the wrapped usb.core.Device instance.
        Refer to the usb.core.Device class for details of the Device class.
        """
        return self._strip

    def open(self, num_pixels, datapin=18, clockpin=None, order='rgb'):
        """
        Open/initialize the LED string connected to the standard SPI interface.
        :param num_pixels: Number of LEDs in the string
        :param datapin: GPIO pin for data-out. Must be PWM capable. Typically GPIO 18
        which is physical pin 12.
        :param clockpin: Not used, ignored.
        :param order: The color order used by the string.
        :return:
        """
        self._numpixels = num_pixels
        self._order = order
        logger.debug("AdafruitCircuiPythonWS28xxDriver driver adapter")
        logger.debug("num_pixels=%d, order=%s", num_pixels, order)
        if datapin != 18:
            raise ValueError("DataPin value is not supported (only pin 18)")
        # Forced to rgb ordering (which is bgr to the driver)
        # TODO Figue out how to translated "rgb" to tuple
        pixel_order = self._translate_color_order(order)
        # For PWM there is no clock pin, only a data pin
        # Manage a singleton copy of the NeoPixel driver
        if not AdafruitCircuiPythonWS28xxDriver._driver:
            AdafruitCircuiPythonWS28xxDriver._driver = neopixel.NeoPixel(board.D18, num_pixels, pixel_order=pixel_order, auto_write=False)
        self._driver = AdafruitCircuiPythonWS28xxDriver._driver

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
        # Driver brightness is 0.0-1.0, so we simply translate it here
        self._driver.brightness = float(brightness / 255)
        return True

    def setPixelColor(self, index, color_value):
        """
        Set the color of a given pixel
        :param index: pixel 0-n where n = num_pixels - 1
        :param color_value: A color value in the form 0xRRGGBB.
        :return:
        """
        # The Adafruit driver class implements a pixel list as its basic behavior
        self._driver[index] = color_value
        return True

    def clear(self):
        """
        Set all pixels to off.
        :return:
        """
        self._driver.fill(0)
        self._driver.show()
        return True

    def close(self):
        """
        Close and release the current device.
        :return: None
        """
        # self.clear()
        # self._driver.deinit();
        # del self._driver
        self._driver = None
        logger.debug("AdafruitCircuiPythonWS28xxDriver closed")
        return True

    def color(self, r, g, b, gamma=False):
        # Based on empiracle observation when the order is rgb
        # when order='rgb'
        if gamma:
            return (self.gamma8[b] << 16) | (self.gamma8[g] << 8) | self.gamma8[r]
        return (b << 16) | (g << 8) | r
    
    @classmethod
    def _translate_color_order(cls, order):
        if len(order) == 3:
            one = cls._color_order[order[0]]
            two = cls._color_order[order[1]]
            three = cls._color_order[order[2]]
            return (one, two, three)
        # RGB default
        return (2, 1, 0)

