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

#
# LED interface driver template
#

class DummyDriver:
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
        self._order = 'rgb'
        self._datapin = 10
        self._clockpin = 11
        self._numpixels = 30

    @property
    def Device(self):
        """
        Returns the wrapped usb.core.Device instance.
        Refer to the usb.core.Device class for details of the Device class.
        """
        return self._strip

    def open(self, num_pixels, datapin=10, clockpin=11, order='rgb'):
        self._numpixels = num_pixels
        return self._begin()

    def _begin(self):
        return True

    def show(selfself):
        return True

    def numPixels(self):
        return self._numpixels

    def setBrightness(self, brightness):
        return True

    def setPixelColor(self, index, color_value):
        return True

    def clear(self):
        return True

    def close(self):
        """
        Close and release the current usb device.
        :return: None
        """
        return True

    def color(self, r, g, b, gamma=False):
        # Based on empiracle observation when the order is rgb
        # when order='rgb'
        if gamma:
            return (DummyDriver.gamma8[b] << 16) | (DummyDriver.gamma8[g] << 8) | DummyDriver.gamma8[r]
        return (b << 16) | (g << 8) | r
