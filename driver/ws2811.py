#
# AtHomeLED - LED interface driver template
# Copyright (C) 2016  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

# The neopixel module comes from the rpi_ws281x repo. The original
# repo can be found at https://github.com/jgarff/rpi_ws281x. A fork
# of the original repo is at https://github.com/dhocker/rpi_ws281x
import rpi_ws281x
from .driver_base  import DriverBase

#
# LED interface driver for WS2811 controlled strips and strings
#

class WS2811(DriverBase):
    """
    A device driver must implement each of the methods in this class.
    The driver class name is arbitrary and generally is not exposed.
    Add the driver to the app by modifying the driver.get_driver()
    method.
    """

    def __init__(self):
        DriverBase.__init__(self)
        self._datapin = 18

    @property
    def name(self):
        return "WS2811Driver"

    def open(self, num_pixels, datapin=18, order='rgb'):
        """
        Open the device
        :param num_pixels: Total number of pixes on the strip/string
        :param datapin: Must be a pin that supports PWM. Pin 18 is the only
        pin on the RPi that supports PWM.
        :param order: Required for interface compatibility. Not used.
        :return:
        """
        self._strip = rpi_ws281x.Adafruit_NeoPixel(num_pixels, datapin, dma=10)
        # print self._strip
        self._numpixels = num_pixels
        self._datapin = datapin
        return self._begin()

    def _begin(self):
        # The begin() method does not return a useful value
        self._strip.begin()
        return True

    def show(self):
        return self._strip.show() == 0
        return True

    def numPixels(self):
        return self._numpixels

    def setBrightness(self, brightness):
        self._strip.setBrightness(brightness)
        return True

    def setPixelColor(self, index, color_value):
        if index >= self._numpixels:
            # TODO Change this to a log record
            # print "Pixel index out of range"
            return False
        else:
            self._strip.setPixelColor(index, color_value)
        return True

    def clear(self):
        for i in range(self._numpixels):
            self._strip.setPixelColor(i, 0)
        self._strip.show()
        return True

    def close(self):
        """
        Close and release the current device.
        :return: None
        """
        self._strip = None
        return True

    def color(self, r, g, b, gamma=False):
        """
        Create a composite RGB color value
        :param r: 0-255
        :param g: 0-255
        :param b: 0-255
        :param gamma: If True, gamma correction is applied.
        :return:
        """
        # Note that this IS NOT the same order as the DotStar
        if gamma:
            return (WS2811._gamma8[r] << 16) | (WS2811._gamma8[g] << 8) | WS2811._gamma8[b]
        return (r << 16) | (g << 8) | b

