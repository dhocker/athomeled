#
# LED interface driver for LED Emulator app
# Copyright (C) 2016  Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

import socket
from struct import pack
from .driver_base import DriverBase

#
# LED interface driver for APA102 controlled strips and strings
# DotStar strips are a popular example
#

class LEDEmulator(DriverBase):
    """
    A device driver must implement each of the methods in the DriverBase class.
    The driver class name is arbitrary and generally is not exposed.
    Add the driver to the app by modifying the manager.get_driver()
    method (the driver factory).
    """

    def __init__(self):
        DriverBase.__init__(self)

    @property
    def name(self):
        return "LEDEmulator"

    def open(self, num_pixels, order='rgb'):
        """
        Open the device
        :param num_pixels: Total number of pixels on the strip/string.
        :param order: The order of colors as expected by the strip/string.
        :return:
        """
        self._numpixels = num_pixels
        self._brightness = 31

        # Create the APA102-like LED data frame
        # The frame is a list so the elements can be assigned
        self._frame = [0, 0, 0, 0]
        for i in range(num_pixels):
            self._frame.extend([0xE0 + self._brightness, 0, 0, 0])
        self._frame.extend([0xFF, 0xFF, 0xFF, 0xFF])

        return self._begin()

    def _begin(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print("Connecting...")
            self._sock.connect(("localhost", 5555))
            print("Connected")
        except Exception as ex:
            print(str(ex))
            return False
        return True

    def _set_pixel(self, index, r, g, b):
        if r > 255 or g > 255 or b > 255:
            raise ValueError("RGB out of range:", r, g, b)
        px = 4 + (index * 4)
        self._frame[px] = 0xE0 + self._brightness
        self._frame[px + 1] = r
        self._frame[px + 2] = g
        self._frame[px + 3] = b

    def show(self):
        # Convert the frame as a list to a string of bytes
        frame_bytes = bytes(self._frame)
        LEDEmulator.frame_send(self._sock, frame_bytes)

        return True

    def numPixels(self):
        return self._numpixels

    def setBrightness(self, brightness):
        """
        Set global brightness level
        :param brightness: 0 - 255
        :return:
        """
        if brightness < 0 or brightness > 255:
            raise ValueError("Brightness out of range")
        # Since we are emulating an APA102 string, the max brightness is 31.
        # We simply scale the brightness value.
        self._brightness = int(brightness / 8)
        return True

    def setPixelColor(self, index, color_value):
        if index < 0 or index < self._numpixels:
            rgb = LEDEmulator.rgb_from_color(color_value)
            self._set_pixel(index, rgb[0], rgb[1], rgb[2])
            return True
        raise ValueError("Index is out of range")

    def clear(self):
        for i in range(self._numpixels):
            self._set_pixel(i, 0, 0, 0)
        return self.show()

    def close(self):
        """
        Close and release the current device.
        :return: None
        """
        return self._sock.close()

    @staticmethod
    def frame_send(sock, frame):
        LEDEmulator.block_send(sock, len(frame))
        LEDEmulator.block_send(sock, frame)

    @staticmethod
    def block_send(sock, block):
        total_sent = 0
        if isinstance(block, int):
            block = pack('!i', block)
        while total_sent < len(block):
            sent = sock.send(block[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    @staticmethod
    def color(r, g, b, gamma=False):
        """
        Create a composite RGB color value
        :param r: 0-255
        :param g: 0-255
        :param b: 0-255
        :param gamma: If True, gamma correction is applied.
        :return:
        """
        return (r << 16) | (g << 8) | b

    @staticmethod
    def rgb_from_color(color):
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        return r, g, b
