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

import neopixel

#
# LED interface driver for WS2811 controlled strips and strings
#

class WS2811:
    """
    A device driver must implement each of the methods in this class.
    The driver class name is arbitrary and generally is not exposed.
    Add the driver to the app by modifying the driver.get_driver()
    method.

    This template is implemented as a dummy device driver for testing.
    """

    #
    # Gamma correction table
    # See https://learn.adafruit.com/led-tricks-gamma-correction/the-issue
    #
    gamma8 = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2,
        2, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5,
        5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10,
        10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
        17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
        25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
        37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
        51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
        69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
        90, 92, 93, 95, 96, 98, 99, 101, 102, 104, 105, 107, 109, 110, 112, 114,
        115, 117, 119, 120, 122, 124, 126, 127, 129, 131, 133, 135, 137, 138, 140, 142,
        144, 146, 148, 150, 152, 154, 156, 158, 160, 162, 164, 167, 169, 171, 173, 175,
        177, 180, 182, 184, 186, 189, 191, 193, 196, 198, 200, 203, 205, 208, 210, 213,
        215, 218, 220, 223, 225, 228, 231, 233, 236, 239, 241, 244, 247, 249, 252, 255]

    def __init__(self):
        self._strip = None
        self._datapin = 18
        self._numpixels = 30

    @property
    def Device(self):
        """
        Returns the wrapped usb.core.Device instance.
        Refer to the usb.core.Device class for details of the Device class.
        """
        return self._strip

    def open(self, num_pixels, datapin=18, order='rgb'):
        """
        Open the device
        :param num_pixels: Total number of pixes on the strip/string
        :param datapin: Must be a pin that supports PWM. Pin 18 is the only
        pin on the RPi that supports PWM.
        :param order: Required for interface compatibility. Not used.
        :return:
        """
        self._strip = neopixel.Adafruit_NeoPixel(num_pixels, datapin)
        self._numpixels = num_pixels
        return self._begin()

    def _begin(self):
        return self._strip.begin() == 0

    def show(self):
        return self._strip.show() == 0

    def numPixels(self):
        return self._numpixels

    def setBrightness(self, brightness):
        self._strip.setBrightness(brightness)
        return True

    def setPixelColor(self, index, color_value):
        self._strip.setPixelColor(index, color)
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
            return (WS2811.gamma8[r] << 16) | (WS2811.gamma8[g] << 8) | WS2811.gamma8[b]
        return (r << 16) | (g << 8) | b

