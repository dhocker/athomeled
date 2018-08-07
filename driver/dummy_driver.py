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

from .driver_base import DriverBase

#
# LED interface driver template
#

class DummyDriver(DriverBase):
    """
    A device driver must implement each of the methods in this class.
    The driver class name is arbitrary and generally is not exposed.
    Add the driver to the app by modifying the driver.get_driver()
    method.

    This template is implemented as a dummy device driver for testing.
    """

    def __init__(self):
        DriverBase.__init__(self)

    @property
    def name(self):
        return "DummyDeviceDriver"

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

    def show(self):
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
