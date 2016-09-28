#
# AtHomeLED - LED interface driver for APA102/dotstar strips/strings
# Copyright (C) 2016  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

# The dotstar module comes from the Adafruit_DotStar_Pi repo. The original
# repo can be found at https://github.com/adafruit/Adafruit_DotStar_Pi. A fork
# of the original repo is at https://github.com/dhocker/Adafruit_DotStar_Pi
from dotstar import Adafruit_DotStar
from driver_base import DriverBase

#
# LED interface driver for APA102 controlled strips and strings
# DotStar strips are a popular example
#

class DotStar(DriverBase):
    """
    A device driver must implement each of the methods in the DriverBase class.
    The driver class name is arbitrary and generally is not exposed.
    Add the driver to the app by modifying the manager.get_driver()
    method (the driver factory).
    """

    def __init__(self):
        DriverBase.__init__(self)

    def open(self, num_pixels, order='rgb'):
        """
        Open the device
        :param num_pixels: Total number of pixels on the strip/string.
        :param order: The order of colors as expected by the strip/string.
        :return:
        """
        self._strip = Adafruit_DotStar(num_pixels, order=order)
        # print self._strip
        self._numpixels = num_pixels
        return self._begin()

    def _begin(self):
        # The begin() method does not return a useful value
        self._strip.begin()
        return True

    def show(self):
        return self._strip.show() == 0

    def numPixels(self):
        return self._numpixels

    def setBrightness(self, brightness):
        self._strip.setBrightness(brightness)
        return True

    def setPixelColor(self, index, color_value):
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
        del self._strip
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
            return (DotStar._gamma8[r] << 16) | (DotStar._gamma8[g] << 8) | DotStar._gamma8[b]
        return (r << 16) | (g << 8) | b

